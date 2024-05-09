from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        page_sze = 100

        # get some public transaction data
        tx_count = self.tenscan_get_total_transactions()         # independent check on num tx transactions
        num_pages = int((tx_count / page_sze) + 1)               # expected number of pages to call
        residual = int(tx_count % page_sze)                      # the residual amount in the last page
        start_page = (num_pages-5) if (num_pages > 5) else 0     # start requesting pages from this value
        pages = range(start_page, num_pages)                     # the pages we are going to request
        self.log.info('Total transaction count:      %d', tx_count)
        self.log.info('Total number of pages:        %d', num_pages)
        self.log.info('Residual number in last page: %d', residual)
        self.log.info('The pages requested:          %d', pages)

        # get the pages
        total = 0
        tx_data = []
        pages = range(start_page, num_pages)
        for page in pages:
            tx_data = self.scan_get_public_transaction_data(page, page_sze)
            total = total + len(tx_data['TransactionsData'])
            self.log.info('Processed page %d, total is %d', page, total)

        # assert we get the expected amount over the last pages
        self.assertTrue(len(tx_data) == (len(pages)-1)*page_sze + residual)
