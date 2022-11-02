import os
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.relevancy.relevancy import Relevancy
from obscuro.test.helpers.wallet_extension import WalletExtension


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = Obscuro
        web3, account = network.connect_game_user(self)

        # deploy the storage contract
        contract = Relevancy(self, web3)
        contract.deploy(network, account)

        # run the javascript event log subscriber in the background for the other accounts
        self.subscribe(network, Properties().gameuserpk(), 'gameuser', contract)
        self.subscribe_separate_wallet(Properties().account1pk(), 'account1', contract)
        self.subscribe_separate_wallet(Properties().account2pk(), 'account2', contract)
        self.subscribe_separate_wallet(Properties().account3pk(), 'account3', contract)

        # perform some transactions
        self.log.info('Performing transactions ... ')
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account, contract.GAS)

        # unpleasant sleep but want to ensure transaction is propagated
        self.wait(5)

        # wait and assert that the game user does see this event
        self.waitForGrep(file='subscriber_gameuser.out', expr='Received event: CallerIndexedAddress', timeout=10)
        self.assertGrep(file='subscriber_gameuser.out', expr='Received event: CallerIndexedAddress')

        # ensure that the other users don't see it
        self.assertGrep(file='subscriber_account1.out', expr='Received event: CallerIndexedAddress', contains=False)
        self.assertGrep(file='subscriber_account2.out', expr='Received event: CallerIndexedAddress', contains=False)
        self.assertGrep(file='subscriber_account3.out', expr='Received event: CallerIndexedAddress', contains=False)

    def subscribe(self, network, pk_to_register, name, contract):
        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber_%s.out' % name)
        stderr = os.path.join(self.output, 'subscriber_%s.err' % name)
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_http', network.connection_url(web_socket=False)])
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', contract.contract_address])
        args.extend(['--contract_abi', contract.abi_path])
        args.extend(['--pk_to_register', pk_to_register])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscription confirmed with id:', timeout=10)

    def subscribe_separate_wallet(self, pk_to_register, name, contract):
        # create a unique wallet extension for this client
        http_port = self.getNextAvailableTCPPort()
        ws_port = self.getNextAvailableTCPPort()
        extension = WalletExtension(self, http_port, ws_port, name=name)
        extension.run()

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber_%s.out' % name)
        stderr = os.path.join(self.output, 'subscriber_%s.err' % name)
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_http', 'http://127.0.0.1:%d' % http_port])
        args.extend(['--network_ws', 'ws://127.0.0.1:%d' % ws_port])
        args.extend(['--contract_address', contract.contract_address])
        args.extend(['--contract_abi', contract.abi_path])
        args.extend(['--pk_to_register', pk_to_register])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscription confirmed with id:', timeout=10)
