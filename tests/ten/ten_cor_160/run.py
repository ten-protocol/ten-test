from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # this actually just returns the header of the latest rollup
        rollup_header = self.scan_get_latest_rollup_header()

        rollup = self.scan_get_rollup_by_hash(hash=rollup_header['hash'])
        self.log.info('First rollup %r, second rollup %r' % (rollup_header['hash'], rollup['Header']['hash']))
        self.assertTrue(rollup_header['hash'] == rollup['Header']['hash'], assertMessage='Hashes should match')
