from obscuro.test.basetest import ObscuroTest
from obscuro.test.contracts.guesser.guesser_constructor import GuesserConstructor
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        guesser = GuesserConstructor(self, web3, 0, 100)
        guesser.deploy(network, account)

        # guess the number
        self.log.info('Starting guessing game')
        self.assertTrue(guesser.guess() == guesser.secret)
