from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import ZeroEventSigGuessGame


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # player 1 deploys the contract and subscribes for events
        game = ZeroEventSigGuessGame(self, web3)
        game.deploy(network, account)
        for i in range(1, 3):
            self.log.info('Number to guess is %d', i)
            network.transact(self, web3, game.contract.functions.guess(i), account, game.GAS_LIMIT)

        self.addOutcome(PASSED)
