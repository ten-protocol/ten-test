from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.game.token import Token
from obscuro.test.contracts.game.game import Game
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        token = Token(self, web3)
        token.deploy(network, account)

        game = Game(self, web3, 10, token.address)
        game.deploy(network, account)
