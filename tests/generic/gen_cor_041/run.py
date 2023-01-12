from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.guesser.guesser_constructor import GuesserConstructor
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        guesser = GuesserConstructor(self, web3, 0, 100)
        guesser.deploy(network, account)

        # guess the number
        self.log.info('Starting guessing game')
        self.assertTrue(guesser.guess() == guesser.secret)
