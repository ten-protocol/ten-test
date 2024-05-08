from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        page_sze = 100

        # get some public transaction data
        tx_count = self.tenscan_get_total_transactions()
        num_pages = int((tx_count / page_sze) + 1)
        residual = int(tx_count % page_sze)
        self.log.info('Total transaction count: %d', tx_count)
        self.log.info('Total number of pages: %d', num_pages)
        self.log.info('last residual page: %d', residual)

        total = 0
        tx_data = []
        for page in range(0, num_pages):
            tx_data = self.scan_get_public_transaction_data(page, page_sze)
            total = total + len(tx_data['TransactionsData'])
            self.log.info('Processed page %d, total is %d', page, total)

        self.assertTrue(total == tx_count)
        self.assertTrue(len(tx_data) == residual)
