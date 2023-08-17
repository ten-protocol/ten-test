import random
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.guesser import GuesserConstructor


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        value = random.randint(0, 99)
        guesser = GuesserConstructor(self, web3, value)
        guesser.deploy(network, account)

        # guess the number
        self.log.info('Starting guessing game')
        self.assertTrue(guesser.guess(0, 100) == value)
