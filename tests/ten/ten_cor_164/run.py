from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # user deploys the contract and performs some transactions against it
        game = TransparentGuessGame(self, web3)
        game.deploy(network, account)
        network.transact(self, web3, game.contract.functions.guess(1), account, game.GAS_LIMIT)
        network.transact(self, web3, game.contract.functions.guess(2), account, game.GAS_LIMIT)

        # call to get personal transactions
        self.scan_get_personal_transactions(address=account.address)

