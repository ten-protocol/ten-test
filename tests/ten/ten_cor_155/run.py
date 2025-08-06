from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # this actually just returns the header of the latest batch
        batch = self.scan_get_latest_batch()
        batch_number1 = int(batch['number'], 16)

        self.wait(2*float(self.block_time))
        batch = self.scan_get_latest_batch()
        batch_number2 = int(batch['number'], 16)

        self.log.info('First batch %d, second batch %d' % (batch_number1, batch_number2))
        self.assertTrue(batch_number2 > batch_number1, assertMessage='Latest batch number should increase')