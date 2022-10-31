from web3 import Web3
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.helpers.log_subscriber import EventLogSubscriber
from obscuro.test.helpers.wallet_extension import WalletExtension


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = Obscuro
        web3, account = network.connect_game_user(self)

        # deploy the storage contract
        key_storage = KeyStorage(self, web3)
        key_storage.deploy(network, account)

        self.subscribe(network, Properties().account1pk(), 'account1')
        self.subscribe(network, Properties().account2pk(), 'account2')
        self.subscribe(network, Properties().account3pk(), 'account3')

    def subscribe(self, network, pk_to_register, name):
        # create a unique wallet extension for this client
        http_port = self.getNextAvailableTCPPort()
        ws_port = self.getNextAvailableTCPPort()
        extension = WalletExtension(self, http_port, ws_port)
        extension.run()

        # run the javascript event log subscriber in the background
        subscriber = EventLogSubscriber(self, network, stdout='%s.out' % name, stderr='%s.err' % name)
        subscriber.run(
            network_ws='ws://127.0.0.1:%d' % ws_port,
            network_http='http://127.0.0.1:%d' % http_port,
            pk_to_register=pk_to_register,
            filter_topics=[Web3().keccak(text='Stored(uint256)').hex()]
        )
        subscriber.subscribe()