from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        # this actually just returns the header of the latest rollup
        rollup_header = self.scan_get_latest_rollup_header()

        if rollup_header is not None:
            rollup = self.scan_get_rollup_by_hash(hash=rollup_header['hash'])
            self.log.info('First rollup %r, second rollup %r' % (rollup_header['hash'], rollup['Header']['hash']))
            self.assertTrue(rollup_header['hash'] == rollup['Header']['hash'], assertMessage='Hashes should match')
        else:
            self.log.warn('latest rollup header is None - this maybe because there are no rollups yet')
