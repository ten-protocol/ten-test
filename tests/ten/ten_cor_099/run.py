import sys, re
from pysys.constants import FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import MaliciousTransparentConfigGuessGame


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network_1 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        network_2 = self.get_network_connection()
        web3_2, account_2 = network_2.connect_account2(self)

        # player 1 deploys the contract
        game_1 = MaliciousTransparentConfigGuessGame(self, web3_1)
        tx_receipt = game_1.deploy(network_1, account_1, store=True)
        gas_used = tx_receipt['gasUsed']
        gas_supplied = network_1.last_tx[0]
        self.log.info('Gas supplied = %d, gas used = %d', gas_supplied, gas_used)

        # player 2 tries to get the secret number, but it should fail
        game_2 = MaliciousTransparentConfigGuessGame.clone(web3_2, account_2, game_1)
        try:
            int.from_bytes(web3_2.eth.get_storage_at(game_2.address, 1), sys.byteorder)
            self.addOutcome(FAILED, outcomeReason='Contract should default to private')
        except ValueError as e:
            self.log.info('Exception type: %s', type(e).__name__)
            self.log.info('Exception args: %s', e.args)
            regex = re.compile('eth_getStorageAt is not supported for this contract', re.M)
            self.assertTrue(regex.search(e.args[0]['message']) is not None)

        # player 1 should have had all their gas burned
        self.assertTrue(gas_used == gas_supplied, assertMessage='All the gas should have been used')
