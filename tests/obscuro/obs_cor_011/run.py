from pysys.constants import PASSED
from obscuro.test.basetest import ObscuroNetworkTest


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        txs = self.get_latest_transactions(1)
        self.log.info('Last transactions are %s', txs)
        if len(txs) >= 1:
            batch = self.get_batch_for_transaction(txs[0])
            parent_hash = batch['Header']['parentHash']
            number = batch['Header']['number']
            num_tx = len(batch['TxHashes'])
            self.log.info('Parent hash: %s, Number: %d, Ntx: %d', parent_hash, number, num_tx)

            count = 100
            while count > 0:
                self.log.info('Calling to get batch for parent %s', parent_hash)
                batch = self.get_batch(parent_hash)
                if number == 0:
                    self.log.info('Reached the genesis block so exiting')
                    self.log.info(batch)
                    break
                else:
                    parent_hash = batch['Header']['parentHash']
                    number = batch['Header']['number']
                    num_tx = len(batch['TxHashes'])
                    self.log.info('Parent hash: %s, Number: %d, Ntx: %d', parent_hash, number, num_tx)

                count = count - 1

            # in case we didn't reach the genesis block give is a go
            parent_hash = '0x0000000000000000000000000000000000000000000000000000000000000000'
            self.log.info('Calling to get batch for parent %s', parent_hash)
            batch = self.get_batch(parent_hash)
            self.log.info('Genesis batch is %s', batch)

            # if we get this far we've passed
            self.addOutcome(PASSED)