from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # get the latest rollup and from that the first and last batch sequence numbers
        rollup_header = self.scan_get_latest_rollup_header()
        rollup_hash = rollup_header['hash']
        first = int(rollup_header['FirstBatchSeqNo'])
        last = int(rollup_header['LastBatchSeqNo'])
        total = last - first
        self.log.info('First and last batch seq nos are %d %d, total %d', first, last, total)
        self.log.info(rollup_header)

        # get the rollup again from sequence numbers purported to be in the rollup
        for i in range(first, last+1):
            self.log.info('Getting sequence number %d', i)
            rollup_from_sequence = self.scan_get_rollup_by_seq_no(seq=i)
            self.assertTrue(rollup_from_sequence['Header']['hash'] == rollup_hash,
                            assertMessage='Rollup be seq %d should match original header' % i)
