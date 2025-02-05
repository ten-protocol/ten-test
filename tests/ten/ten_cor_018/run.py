from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # get the receipt sort the fields
        storage_tx_receipt = network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)

