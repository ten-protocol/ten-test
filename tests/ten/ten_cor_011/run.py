from ten.test.contracts.storage import Storage
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        page_num = 0
        page_sze = 100
        max_pages = 250

        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # get some public transaction data
        tx_count = self.tenscan_get_total_transactions()
        num_pages = int((tx_count / page_sze) + 1)
        residual = int(tx_count % page_sze)
        self.log.info('Total transaction count: %d', tx_count)
        self.log.info('Total number of pages: %d', num_pages)
        self.log.info('last residual page: %d', residual)

        total = 0
        broke_out = False
        hashes = []
        for page in range(0, num_pages+200):
            if page > max_pages:
                self.log.info('Exceeded max pages for the test run ... breaking')
                broke_out = True
                break
            tx_data = self.scan_get_public_transaction_data(page, page_sze)
            total = total + len(tx_data['TransactionsData'])
            self.log.info('Seen: %s', (tx_data['TransactionsData'][0] in hashes))
            hashes.extend([x['TransactionHash'] for x in tx_data['TransactionsData']])
            self.log.info(tx_data['TransactionsData'][0]['TransactionHash'])
            self.log.info(tx_data['Total'])
            self.log.info('Processed page %d, total is %d', page, total)

        if not broke_out:
            self.assertTrue(total == tx_count)

        # # deploy the contract make some transactions
        # storage = Storage(self, web3, 100)
        # storage.deploy(network, account)
        # network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        # network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        # network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        # self.wait(float(self.block_time) * 2)
        #
        # # get some public transaction data
        # tx_count = self.tenscan_get_total_transactions()
        # self.log.info('Total transaction count: %d', tx_count)
        #
        # tx_data = self.scan_get_public_transaction_data(0, 100)
        # tot_end = tx_data['Total']
        # txs_end = tx_data['TransactionsData']
        # self.log.info('TXData[\'total\']:  %d', tot_end)
        # self.log.info('Length TXData[\'TransactionsData\']:  %d', len(txs_end))

        # self.assertTrue(tot_end == tot_start+4)
        # self.assertTrue(len(txs_end) <= page_sze)
        # self.assertTrue(len(txs_end) < tot_end)