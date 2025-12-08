from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # retrieve via a call
        self.log.info('Call shows value %d', storage.contract.functions.retrieve().call())

        # set the value via a transaction, compare to call and transaction log
        tx_receipt = network.transact(self, web3, storage.contract.functions.store(200), account, storage.GAS_LIMIT)
        self.log.info('Call shows value %d', storage.contract.functions.retrieve().call())

        tx_log = storage.contract.events.Stored().process_receipt(tx_receipt)[0]
        args_value = tx_log['args']['value']
        self.log.info('Transaction log shows value %d', args_value)
        self.assertTrue(args_value == 200)
