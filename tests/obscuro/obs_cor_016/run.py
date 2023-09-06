from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage import Storage


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network_1 = self.get_network_connection(name='network_1')
        web3_1, account_1 = network_1.connect_account1(self)
        web3_3, account_3 = network_1.connect_account3(self)

        network_2 = self.get_network_connection(name='network_2')
        web3_2, account_2 = network_2.connect_account2(self)

        storage = Storage(self, web3_1, 100)
        storage.deploy(network_1, account_1)

        tx_receipt = network_1.transact(self, web3_1, storage.contract.functions.store(200), account_1, storage.GAS_LIMIT)

        self.log.info('Getting transaction for account 1 (network connection 1)')
        tx = web3_1.eth.get_transaction(tx_receipt.transactionHash)
        self.log.info(tx)
        self.log.info('Getting transaction for account 3 (network connection 1)')
        tx = web3_3.eth.get_transaction(tx_receipt.transactionHash)
        self.log.info(tx)

        response = self.get_debug_log_visibility(tx_receipt.transactionHash.hex())
        self.log.info(response)

        self.log.info('Getting transaction for account 2 (network connection 2)')
        tx = web3_2.eth.get_transaction(tx_receipt.transactionHash)
        self.log.info(tx)
