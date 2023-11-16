from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # get the transaction count and deploy
        storage = Storage(self, web3, 100)
        tx_receipt = storage.deploy(network, account)

        # get the transaction count and interact
        tx = web3.eth.get_transaction(tx_receipt.transactionHash)
        self.assertTrue(tx_receipt.blockHash == tx.blockHash)
        self.assertTrue(tx_receipt.blockNumber == tx.blockNumber)
        self.assertTrue(tx_receipt.transactionHash == tx.hash)
        self.assertTrue(tx_receipt.transactionIndex == tx.transactionIndex)
