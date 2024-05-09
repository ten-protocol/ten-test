from ten.test.contracts.storage import Storage
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        page_sze = 10

        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # get the transaction count
        tot_start = self.tenscan_get_total_transactions()
        self.log.info('Total transaction count: %d', tot_start)

        # deploy the contract make some transactions
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        tx_receipt_1 = network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        tx_receipt_2 = network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        tx_receipt_3 = network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        self.log.info('Submitted transactions:')
        self.log.info('  TX1: %s', tx_receipt_1.transactionHash.hex())
        self.log.info('  TX2: %s', tx_receipt_2.transactionHash.hex())
        self.log.info('  TX3: %s', tx_receipt_3.transactionHash.hex())
        self.wait(float(self.block_time) * 2)

        # get some public transaction data
        tot_end = self.tenscan_get_total_transactions()
        self.log.info('Total transaction count: %d', tot_end)
        tx_data = self.scan_get_public_transaction_data(0, page_sze)
        txs_end = tx_data['TransactionsData']
        txs_hashes = [x['TransactionHash'] for x in txs_end]
        txs_heights = [x['BatchHeight'] for x in txs_end]
        txs_times = [x['BatchTimestamp'] for x in txs_end]
        self.log.info('Public Tx Data total:    %d', tot_end)
        self.log.info('Public Tx Data page:     %d', len(txs_end))
        self.log.info('Returned transactions:')
        for data in txs_end: self.log.info('  %s', data)

        # do a bunch of assertions
        self.assertTrue(tot_end == tot_start+4, assertMessage='Total should increment')

        self.assertTrue(len(txs_end) == page_sze, assertMessage='Return set is page size')
        self.assertTrue(tx_receipt_3.transactionHash.hex() == txs_hashes[0], assertMessage='Tx 3 exists')
        self.assertTrue(tx_receipt_2.transactionHash.hex() == txs_hashes[1], assertMessage='Tx 2 exists')
        self.assertTrue(tx_receipt_1.transactionHash.hex() == txs_hashes[2], assertMessage='Tx 1 exists')
        self.assertTrue(self.is_descending(txs_heights), assertMessage='Tx batch heights are descending')
        self.assertTrue(self.is_descending(txs_times), assertMessage='Tx timestamps are descending')

    def is_descending(self, list):
        return all(list[i] >= list[i+1] for i in range(len(list)-1))
