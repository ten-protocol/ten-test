from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        contracts_before = self.scan_get_total_contract_count()
        transactions_before = self.scan_get_total_transaction_count()
        self.log.info('Total contract count is %d' % contracts_before)
        self.log.info('Total transaction count is %d' % transactions_before)

        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        contracts_after = self.scan_get_total_contract_count()
        transactions_after = self.scan_get_total_transaction_count()
        self.log.info('Total contract count is %d' % contracts_after)
        self.log.info('Total transaction count is %d' % transactions_after)

        for i in range(0,4):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)

        transactions_after_storing = self.scan_get_total_transaction_count()
        self.log.info('Total transaction count is %d' % transactions_after_storing)

        self.assertTrue(contracts_after == (contracts_before + 1))
        self.assertTrue(transactions_after == (transactions_before + 1))
        self.assertTrue(transactions_after_storing == (transactions_after + 4))

