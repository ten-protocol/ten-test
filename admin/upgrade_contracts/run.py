from ten.test.basetest import TenNetworkTest
from ten.test.contracts.guesser import Guesser
from ten.test.helpers.upgrade import UpgradeL1ContractsHelper


class PySysTest(TenNetworkTest):

    def execute(self):
        # create the helper and run the upgrade
        helper = UpgradeL1ContractsHelper(self)
        helper.run()

        # perform some simple transactions
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        guesser = Guesser(self, web3)
        guesser.deploy(network, account)

        # guess the number
        self.log.info('Starting guessing game')
        self.assertTrue(guesser.guess(0, 100) == 12)


