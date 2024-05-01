from ten.test.contracts.storage import Storage
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        page_num = 0
        page_sze = 100

        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # get some public transaction data
        tx_data = self.scan_get_public_transaction_data(page_num, page_sze)
        tot_start = tx_data['Total']
        txs_start = tx_data['TransactionsData']
        self.log.info('TXData[\'total\']:  %d', tot_start)
        self.log.info('Length TXData[\'TransactionsData\']:  %d', len(txs_start))

        # deploy the contract make some transactions
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 2)

        # get some public transaction data
        tx_data = self.scan_get_public_transaction_data(0, 100)
        tot_end = tx_data['Total']
        txs_end = tx_data['TransactionsData']
        self.log.info('TXData[\'total\']:  %d', tot_end)
        self.log.info('Length TXData[\'TransactionsData\']:  %d', len(txs_end))

        self.assertTrue(tot_end == tot_start+4)
        self.assertTrue(len(txs_end) <= page_sze)
        self.assertTrue(len(txs_end) < tot_end)