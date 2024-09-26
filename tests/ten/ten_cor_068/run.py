from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame
from web3._utils.events import EventLogErrorFlags


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect the dev to the network to deploy the game
        network_dev = self.get_network_connection()
        web3_dev, account_dev = network_dev.connect_account2(self)
        game = TransparentGuessGame(self, web3_dev)
        game.deploy(network_dev, account_dev)

        # connect a user to the network to play the game and make some guesses
        network_usr = self.get_network_connection()
        web3_usr, account_usr = network_usr.connect_account1(self)
        game_usr = TransparentGuessGame.clone(web3_usr, account_usr, game)
        tx_rcpt = network_dev.transact(self, web3_usr, game_usr.contract.functions.guess(2), account_usr, game_usr.GAS_LIMIT)

        receipt = web3_dev.eth.get_transaction_receipt(tx_rcpt.transactionHash)
        logs = game.contract.events.Guessed().process_receipt(receipt, EventLogErrorFlags.Discard)
        self.assertTrue(logs[0]['args']['guessedNumber'] == 2, assertMessage='Logs should show the guessed number as 2')
