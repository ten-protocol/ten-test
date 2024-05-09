import math
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        page_sze = 3

        # get some public transaction data
        tx_count = self.tenscan_get_total_transactions()         # independent check on num tx transactions
        pages = self.split_into_segments(tx_count, page_sze)[-2:]
        self.log.info('Total transaction count:            %d', tx_count)
        self.log.info('Page size being used:               %d', page_sze)
        self.log.info('Total number of pages:              %d', len(pages))
        self.log.info('Last (Offset, sizes) requested:     %s', pages)

        # get the pages
        total = 0
        expected = 0
        for page in pages:
            tx_data = self.scan_get_public_transaction_data(page[0], page[1])
            total = total + len(tx_data['TransactionsData'])
            expected = expected + page[1]
            self.log.info('Processed offset %d, number returned %d', page[0], len(tx_data['TransactionsData']))

        # assert we get the expected amount over the last pages
        self.assertTrue(total == expected)

        # assert no overflow in calling for the transactions
        tx_data = self.scan_get_public_transaction_data(tx_count, page_sze)
        self.assertTrue(tx_data['TransactionsData'] is None)

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