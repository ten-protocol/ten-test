import os
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.relevancy.relevancy import Relevancy


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
        self.subscribe(network, Properties().account1pk(), 'account1', contract)
        self.subscribe(network, Properties().account2pk(), 'account2', contract)
        self.subscribe(network, Properties().account3pk(), 'account3', contract)

        # perform some transactions
        self.log.info('Performing transactions ... ')
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account, contract.GAS)
        self.waitForGrep(file='subscriber_gameuser.out', expr='Received event: CallerIndexedAddress', timeout=10)
        self.assertGrep(file='subscriber_gameuser.out', expr='Received event: CallerIndexedAddress')
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
