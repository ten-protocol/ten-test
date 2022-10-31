from web3 import Web3
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.relevancy.relevancy import Relevancy
from obscuro.test.helpers.log_subscriber import EventLogSubscriber
from obscuro.test.helpers.wallet_extension import WalletExtension


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = Obscuro
        web3, account = network.connect_game_user(self)
        account1 = Web3().eth.account.privateKeyToAccount(Properties().account1pk()).address
        account2 = Web3().eth.account.privateKeyToAccount(Properties().account2pk()).address
        account3 = Web3().eth.account.privateKeyToAccount(Properties().account3pk()).address
        self.log.info('Account 1 addr: %s' % account1)
        self.log.info('Account 2 addr: %s' % account2)
        self.log.info('Account 3 addr: %s' % account3)

        # deploy the storage contract
        contract = Relevancy(self, web3)
        contract.deploy(network, account)

        # run the javascript event log subscriber in the background
        subscriber = EventLogSubscriber(self, network)
        subscriber.run(pk_to_register=Properties().gameuserpk())
        subscriber.subscribe()

        self.subscribe(network, Properties().account1pk(), 'account1')
        self.subscribe(network, Properties().account2pk(), 'account2')
        self.subscribe(network, Properties().account3pk(), 'account3')

        # perform some transactions
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account, contract.GAS)
        self.wait(2)

    def subscribe(self, network, pk_to_register, name):
        # create a unique wallet extension for this client
        http_port = self.getNextAvailableTCPPort()
        ws_port = self.getNextAvailableTCPPort()
        extension = WalletExtension(self, http_port, ws_port, name=name)
        extension.run()

        # run the javascript event log subscriber in the background
        subscriber = EventLogSubscriber(self, network, stdout='subscriber_%s.out' % name, stderr='subscriber_%s.err' % name)
        subscriber.run(
            network_ws='ws://127.0.0.1:%d' % ws_port,
            network_http='http://127.0.0.1:%d' % http_port,
            pk_to_register=pk_to_register
        )
        subscriber.subscribe()
