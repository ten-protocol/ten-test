from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # this actually just returns the header of the latest batch
        block = self.scan_get_latest_batch()
        block_number1 = int(block['number'], 16)

        self.wait(2*float(self.block_time))
        block = self.scan_get_latest_batch()
        block_number2 = int(block['number'], 16)

        self.log.info('First block %d, second block %d' % (block_number1, block_number2))
        self.assertTrue(block_number2 > block_number1, assertMessage='Latest block number should increase')