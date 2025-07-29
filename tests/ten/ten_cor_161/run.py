from collections import Counter
from pysys.constants import FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # this actually just returns the header of the latest rollup
        rollup_header = self.scan_get_latest_rollup_header()

        batches = self.scan_get_rollup_batches(hash=rollup_header['hash'], offset=0, size=10)
        self.assertTrue(len(batches['BatchesData']) <= 10, assertMessage='Batches should be less than or equal the page')

        for batch in batches['BatchesData']: self.log.info(batch)
