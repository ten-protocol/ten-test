import time
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):
    DURATION = 75 # in 150 secs set 175 as threshold, scale down by 2
    INTERVAL = 5
    THRESHOLD = 88

    def execute(self):
        start = time.time()
        start_txs = int(self.scan_get_approx_total_transaction_count())
        start_bts = int(self.scan_get_batch_listing(size=2)['Total'])

        while True:
            txs = int(self.scan_get_approx_total_transaction_count())
            bts = int(self.scan_get_batch_listing(size=2)['Total'])
            self.log.info(self.scan_get_batch_listing(size=2))
            elapsed = (time.time() - start)
            self.log.info('Elapsed %.2f, txs=%d, batches=%d', elapsed, txs, bts)
            if elapsed > self.DURATION: break
            time.sleep(self.INTERVAL)

        self.assertTrue((bts-start_bts) < self.THRESHOLD,
                        assertMessage='Batch change %d is below threshold %s' % ((bts-start_bts), self.THRESHOLD))
