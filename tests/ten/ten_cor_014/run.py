from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        tx_receipt = network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        entries = list(tx_receipt.keys())
        entries.sort()
        self.log.info(entries)