from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # log the contracts before, deploy contract, and log contracts after
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

        # perform some more transactions and then log the before and after transaction count
        for i in range(0,4):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)

        transactions_after_storing = self.scan_get_total_transaction_count()
        self.log.info('Total transaction count is %d' % transactions_after_storing)

        self.assertTrue(contracts_after == (contracts_before + 1))
        self.assertTrue(transactions_after == (transactions_before + 1))
        self.assertTrue(transactions_after_storing == (transactions_after + 4))

