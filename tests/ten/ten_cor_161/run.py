from collections import Counter
from pysys.constants import FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the latest rollup and from that the first and last batch sequence numbers
        rollup_header = self.scan_get_latest_rollup_header()
        first = int(rollup_header['FirstBatchSeqNo'])
        last = int(rollup_header['LastBatchSeqNo'])
        total = last - first
        self.log.info('First and last batch seq nos are %d %d, total %d', first, last, total)

        batches = []
        for page in self.split_into_segments(total, 10):
            self.log.info(' Getting page with offset and size %d %d', page[0], page[1])
            batches.extend(self.scan_get_rollup_batches(hash=rollup_header['hash'], offset=page[0], size=page[1])['BatchesData'])

        self.assertTrue(len(batches) <= total, assertMessage='Batches should be less than or equal to the page size')
        batch_nos = [int(x['header']['number'], 16) for x in batches]
        self.log.info('Batch numbers are %s', batch_nos)
        self.assertTrue(batch_nos[0] == last, assertMessage='Last batch should be in the return set')
        self.assertTrue(batch_nos[-1] == first, assertMessage='First batch should be in the return set')

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