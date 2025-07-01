import os, json
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # player 1 deploys the contract and subscribes for events
        game = TransparentGuessGame(self, web3)
        game.deploy(network, account)
        for i in range(1,5):
            self.log.info('Number to guess is %d', i)
            network.transact(self, web3, game.contract.functions.guess(i), account, game.GAS_LIMIT)

        pk = self.get_ephemeral_pk()
        web_usr, account_usr = network.connect(self, private_key=pk, check_funds=True)

        tx_count = self.scan_get_total_transaction_count()
        pages = self.split_into_segments(tx_count, 20)

        txs = self.scan_list_personal_transactions(url=network.connection_url(), address=account_usr.address,
                                                   offset=pages[-1:][0], size=20)
        tx_hashes = [x['blockHash'] for x in txs['Receipts']]
        self.log.info('Returned block and tx hashes are;')
        for tx in txs['Receipts']: self.log.info('  %s %s' % (tx['blockHash'], tx['transactionHash']))



    def split_into_segments(self, number, increment):
        result = []
        start = 0
        while number > 0:
            if number >= increment:
                result.append((start, increment))
                number -= increment
                start += increment
            else:
                result.append((start, number))
                break
        return result