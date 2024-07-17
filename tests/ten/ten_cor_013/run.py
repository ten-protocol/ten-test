from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # log the contracts before, deploy contract, and log contracts after
        cnt_before_deploy = self.scan_get_total_contract_count()
        txs_before_deploy = self.scan_get_total_transaction_count()
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        cnt_after_deploy = self.scan_get_total_contract_count()
        txs_after_deploy = self.scan_get_total_transaction_count()
        self.log.info('Contract count before deployment:    %d' % cnt_before_deploy)
        self.log.info('Contract count after deployment:     %d' % cnt_after_deploy)
        self.log.info('Transaction count before deployment: %d' % txs_before_deploy)
        self.log.info('Transaction count after deployment:  %d' % txs_after_deploy)

        # perform some more transactions and then log the before and after transaction count
        for i in range(0,4):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)
        txs_after_storing = self.scan_get_total_transaction_count()
        self.log.info('Transaction count after txs: %d' % txs_after_storing)

        self.assertTrue(cnt_after_deploy == (cnt_before_deploy + 1), assertMessage='Contract count should increase by 1 after deploy')
        self.assertTrue(txs_after_deploy == (txs_before_deploy + 1), assertMessage='Tx count should increase by 1 after deploy')
        self.assertTrue(txs_after_storing == (txs_after_deploy + 4), assertMessage='Tx count should increase by 4 after storing')

