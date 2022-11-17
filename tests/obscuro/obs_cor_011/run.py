from obscuro.test.basetest import ObscuroNetworkTest


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        txs = self.get_latest_transactions(1)
        self.log.info('Last transactions are %s' % txs)
        if len(txs) >= 1:
            rollup = self.get_rollup_for_transaction(txs[0])
            parent_hash = rollup['Header']['ParentHash']
            number = rollup['Header']['Number']
            num_tx = len(rollup['TxHashes'])
            self.log.info('Parent hash: %s, Number: %d, Ntx: %d' % (parent_hash, number, num_tx))

            count = 100
            while count > 0:
                self.log.info('Calling to get rollup for parent %s' % parent_hash)
                rollup = self.get_rollup(parent_hash)
                if number == 0:
                    self.log.info('Reached the genesis block so exiting')
                    self.log.info(rollup)
                    break
                else:
                    parent_hash = rollup['Header']['ParentHash']
                    number = rollup['Header']['Number']
                    num_tx = len(rollup['TxHashes'])
                    self.log.info('Parent hash: %s, Number: %d, Ntx: %d' % (parent_hash, number, num_tx))

                count = count - 1

            # in case we didn't reach the genesis block give is a go
            parent_hash = '0x0000000000000000000000000000000000000000000000000000000000000000'
            self.log.info('Calling to get rollup for parent %s' % parent_hash)
            rollup = self.get_rollup(parent_hash)
            self.log.info('Genesis rollup is %s' % rollup)