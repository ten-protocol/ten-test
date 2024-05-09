import math
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        page_sze = 3

        # get some public transaction data
        tx_count = self.tenscan_get_total_transactions()         # independent check on num tx transactions
        num_pages = math.ceil((tx_count / page_sze))             # expected number of pages to call
        last = tx_count - (num_pages-1)*page_sze                 # the last page amount in the last page
        pages = list(range(0, num_pages))[-2:]
        self.log.info('Total transaction count:      %d', tx_count)
        self.log.info('Page size being used:         %d', page_sze)
        self.log.info('Total number of pages:        %d', num_pages)
        self.log.info('Last two pages requested:     %s', pages)
        self.log.info('Last two page sizes:          %s, %s', page_sze, last)

        # get the pages
        total = 0
        for page in pages:
            tx_data = self.scan_get_public_transaction_data(page, page_sze)
            total = total + len(tx_data['TransactionsData'])
            self.log.info('Processed page %d, number returned %d', page, len(tx_data['TransactionsData']))

        # assert we get the expected amount over the last pages
        self.assertTrue(total == page_sze + last)
