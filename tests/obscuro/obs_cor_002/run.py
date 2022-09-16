from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.storage import Storage
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):

    def execute(self):
        # get the game address and the jam token address from the properties
        network = Obscuro
        web3, account = network.connect_account1(self, web_socket=True)

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
