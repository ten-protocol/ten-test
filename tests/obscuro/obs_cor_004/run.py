import os
from web3 import Web3
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.relevancy.relevancy import Relevancy
from obscuro.test.helpers.wallet_extension import WalletExtension


class PySysTest(ObscuroTest):

    def execute(self):
        block_time=Properties().block_time_secs(self.env)

        # connect to network
        network = Obscuro
        web3, account = network.connect_game_user(self)
        account1 = Web3().eth.account.privateKeyToAccount(Properties().account1pk())

        # deploy the storage contract
        contract = Relevancy(self, web3)
        contract.deploy(network, account)

        # run the javascript event log subscriber in the background for the other accounts
        self.subscribe(network, Properties().gameuserpk(), 'gameuser', contract)
        self.subscribe(network, Properties().account1pk(), 'account1', contract, new_wallet=True)
        self.subscribe(network, Properties().account2pk(), 'account2', contract, new_wallet=True)
        self.subscribe(network, Properties().account3pk(), 'account3', contract, new_wallet=True)

        # perform some transactions
        self.log.info('Performing transactions ... ')
        network.transact(self, web3,
                         contract.contract.functions.twoIndexedAddresses(account.address, account1.address),
                         account, contract.GAS)

        # unpleasant sleep the block time + 10%
        self.wait(float(block_time)*1.1)

        # wait and assert that the game user does see this event
        self.waitForGrep(file='subscriber_gameuser.out', expr='Received event: TwoIndexedAddresses', timeout=block_time)
        self.assertGrep(file='subscriber_gameuser.out', expr='Received event: TwoIndexedAddresses')

        # wait and assert that account1 does see this event
        self.waitForGrep(file='subscriber_account1.out', expr='Received event: TwoIndexedAddresses', timeout=block_time)
        self.assertGrep(file='subscriber_account1.out', expr='Received event: TwoIndexedAddresses')

        # assert that the other two users do not see the event
        self.assertGrep(file='subscriber_account2.out', expr='Received event: TwoIndexedAddresses', contains=False)
        self.assertGrep(file='subscriber_account3.out', expr='Received event: TwoIndexedAddresses', contains=False)

    def subscribe(self, network, pk_to_register, name, contract, new_wallet=False):
        network_http = network.connection_url(web_socket=False)
        network_ws = network.connection_url(web_socket=True)

        # if going through a new wallet, start up and reassign the connection URLS from the default
        if new_wallet:
            http_port = self.getNextAvailableTCPPort()
            ws_port = self.getNextAvailableTCPPort()
            network_http = 'http://127.0.0.1:%d' % http_port
            network_ws = 'ws://127.0.0.1:%d' % ws_port
            extension = WalletExtension(self, http_port, ws_port, name=name)
            extension.run()

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber_%s.out' % name)
        stderr = os.path.join(self.output, 'subscriber_%s.err' % name)
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_http', network_http])
        args.extend(['--network_ws', network_ws])
        args.extend(['--contract_address', contract.contract_address])
        args.extend(['--contract_abi', contract.abi_path])
        args.extend(['--pk_to_register', pk_to_register])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscription confirmed with id:', timeout=10)
