import re
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import FieldTopic1GuessGame
from web3._utils.events import EventLogErrorFlags


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect the players to the network
        network_1 = self.get_network_connection()
        network_2 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account2(self)

        # player 1 deploys the contract
        game_1 = FieldTopic1GuessGame(self, web3_1)
        game_1.deploy(network_1, account_1)

        # player 2 transacts with the contract and parses the logs from the tx receipt
        game_2 = FieldTopic1GuessGame.clone(web3_2, account_2, game_1)
        tx_rcpt = network_2.transact(self, web3_2, game_2.contract.functions.guess(2), account_2, game_2.GAS_LIMIT)

        receipt = web3_2.eth.get_transaction_receipt(tx_rcpt.transactionHash)
        logs = game_2.contract.events.Guessed().process_receipt(receipt, EventLogErrorFlags.Discard)
        self.assertTrue(logs[0]['args']['guessedNumber'] == 2, assertMessage='Logs should show the guessed number as 2')
        logs = game_2.contract.events.Attempts().process_receipt(receipt, EventLogErrorFlags.Discard)
        self.assertTrue(logs[0]['args']['attempts'] == 1, assertMessage='Logs should show the number attempts as 1')

        # player 1 tries to get the receipt, because no events are open to them, they will not be able to get it
        try:
            receipt = web3_1.eth.get_transaction_receipt(tx_rcpt.transactionHash)
        except Exception as e:
            self.log.info('Exception type: %s', type(e).__name__)
            self.log.info('Exception args: %s', e.args)
            regex = re.compile('not authorised', re.M)
            self.assertTrue(regex.search(e.args[0]['message']) is not None)
