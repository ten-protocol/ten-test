from pysys.constants import FAILED, PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # first connection through primary gateway used by two accounts (so same token)
        network_1 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_1.connect_account2(self)

        storage_1 = Storage(self, web3_1, 100)
        storage_1.deploy(network_1, account_1)
        storage_2 = Storage.clone(web3_2, account_2, storage_1)

        tx_receipt = network_1.transact(self, web3_1, storage_1.contract.functions.store(128), account_1, storage_1.GAS_LIMIT)
        tx_hash = tx_receipt.transactionHash
        block_number = tx_receipt.blockNumber

        self.log.info('Getting transaction for account 2 (through network connection 1)')
        tx_rec = web3_2.eth.get_transaction_receipt(tx_hash)
        tx_log = storage_2.contract.events.Stored().process_receipt(tx_rec)[0]
        args_value = tx_log['args']['value']
        self.log.info('Transaction log shows value %d', args_value)
        self.assertTrue(args_value == 128)

        # second connection through the primary gateway, one account (different token to previous)
        network_2 = self.get_network_connection()
        web3_3, account_3 = network_2.connect_account3(self)
        storage_3 = Storage.clone(web3_3, account_3, storage_1)

        self.log.info('Getting transaction for account 3 (through network connection 2)')
        try:
            web3_3.eth.get_transaction_receipt(tx_hash)
            self.addOutcome(FAILED, 'We dont expect to be able to get the transaction')
        except:
            self.log.warn('It is not possible to get someone else transaction receipt')
            self.addOutcome(PASSED)

        self.log.info('Attempting to get the past events from the contract instance')
        events = storage_3.contract.events.Stored().get_logs(fromBlock=block_number)
        self.assertTrue(len(events) == 1)
        self.assertTrue(events[0]['args']['value'] == 128)
