from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.guesser import Guesser


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network and deploy the contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        guesser = Guesser(self, web3)
        guesser.deploy(network, account)

        # guess the number
        self.log.info('Starting guessing game')
        self.assertTrue(guesser.guess(0, 100) == 12)
