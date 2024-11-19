from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import GameTwoPhase
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway and deploy the contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        game = GameTwoPhase(self, web3, Properties().L2PublicCallbacks)
        game.deploy(network, account)
