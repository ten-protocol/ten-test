from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.guesser import Guesser
from obscuro.test.helpers.wallet_extension import WalletExtension


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        wallet = WalletExtension.start(self, name='shared')
        network_connection_1 = self.get_network_connection(wallet=wallet)
        network_connection_2 = self.get_network_connection(wallet=wallet)

        web3_1, account_1 = network_connection_1.connect_account1(self)
        web3_2, account_2 = network_connection_1.connect_account2(self)
        web3_3, account_3 = network_connection_2.connect_account3(self)
        web3_4, account_4 = network_connection_2.connect_account4(self)

        guesser = Guesser(self, web3_1)
        guesser.deploy(network_connection_1, account_1)

        # guess the number
        self.log.info('Starting guessing game')
        self.assertTrue(guesser.guess(0, 100) == 12)