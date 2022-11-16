from obscuro.test.basetest import ObscuroNetworkTest


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        sum_transactions = 0
        txs = self.get_latest_transactions(1)
        self.log.info('Last transactions are %s' % txs)
        if len(txs) >= 1:
            rollup = self.get_rollup_for_transaction(txs[0])
            parent_hash = rollup['Header']['ParentHash']
            number = rollup['Header']['Number']
            num_tx = len(rollup['TxHashes'])
            sum_transactions += num_tx
            self.log.info('Parent hash: %s, Number: %d, Ntx: %d' % (parent_hash, number, num_tx))

            while number >= 1:
                self.log.info('Calling to get rollup for number %d' % number)
                rollup = self.get_rollup(parent_hash)
                parent_hash = rollup['Header']['ParentHash']
                number = rollup['Header']['Number']
                num_tx = len(rollup['TxHashes'])
                sum_transactions += num_tx
                self.log.info('Parent hash: %s, Number: %d, Ntx: %d' % (parent_hash, number, num_tx))

            self.log.info('Calling to get rollup for number %d (the genesis block)' % number)
            self.get_rollup(parent_hash) # not throwing an exception is a pass

        num_transactions = self.get_total_transactions()
        self.log.info('Number of transactions is %d' % num_transactions)
        self.log.info('Summed transactions is %d' % sum_transactions)
        self.assertTrue(num_transactions == sum_transactions)