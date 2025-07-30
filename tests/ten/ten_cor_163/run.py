from collections import Counter
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # user deploys the contract and performs some transactions against it
        self.log.info('')
        self.log.info('User deploys transparent contract and submits 5 transactions against it')
        game = TransparentGuessGame(self, web3)
        game.deploy(network, account)

        hashes = []
        for i in range(1,5):
            tx_receipt = network.transact(self, web3, game.contract.functions.guess(i), account, game.GAS_LIMIT)
            hashes.append(tx_receipt.transactionHash.hex())

        # get the latest batch from the latest batch header
        self.log.info('')
        self.log.info('User gets the latest batch and from that the batch transactions')
        batch_header = self.scan_get_latest_batch()
        batch = self.scan_get_batch(hash=batch_header['hash'])
        while len(batch['TxHashes']) == 0:
            self.log.info('Batch %s transactions %s', batch['Header']['hash'], batch['TxHashes'])
            batch = self.scan_get_batch(hash=batch['Header']['parentHash'])
        self.log.info('Batch %s has %d transactions', batch['Header']['hash'], len(batch['TxHashes']))
        total = len(batch['TxHashes'])

        txs = []
        for page in self.split_into_segments(total, 10):
            self.log.info('Getting page with offset and size %d %d', page[0], page[1])
            txs.extend(self.scan_get_batch_transactions(hash=batch['Header']['hash'], offset=page[0], size=page[1])['TransactionsData'])
        txs_hashes = [x['TransactionHash'] for x in txs]
        self.assertTrue(Counter(txs_hashes) == Counter(batch['TxHashes']),
                        assertMessage='The tx hashes in the batch should be the same as the those from the call to get transactions')

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