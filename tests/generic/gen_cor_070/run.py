from obscuro.test.basetest import ObscuroTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # retrieve via a call
        self.log.info('Call shows value %d' % storage.contract.functions.retrieve().call())

        # set the value via a transaction, compare to call and transaction log
        tx_receipt = network.transact(self, web3, storage.contract.functions.store(200), account, storage.GAS)
        self.log.info('Call shows value %d' % storage.contract.functions.retrieve().call())

        tx_log = storage.contract.events.Stored().processReceipt(tx_receipt)[0]
        args_value = tx_log['args']['value']
        self.log.info('Transaction log shows value %d' % args_value)
        self.assertTrue(args_value == 200)
