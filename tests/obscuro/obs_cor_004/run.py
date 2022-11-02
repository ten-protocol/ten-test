import os
from web3 import Web3
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.relevancy.relevancy import Relevancy


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = Obscuro
        web3_1, account_1 = network.connect_account1(self)
        web3_2, account_2 = network.connect_account2(self)
        web3_3, account_3 = network.connect_account1(self)
        web3, account = network.connect_game_user(self)

        # deploy the storage contract
        contract = Relevancy(self, web3)
        contract.deploy(network, account)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_http', network.connection_url(web_socket=False)])
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', contract.contract_address])
        args.extend(['--contract_abi', contract.abi_path])
        args.extend(['--pk_to_register', Properties().gameuserpk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscription confirmed', timeout=10)

        # perform some transactions
        self.log.info('Performing transactions ... ')
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account, contract.GAS)
        self.wait(5)
        self.waitForGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress', timeout=10)
        self.assertGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress')

