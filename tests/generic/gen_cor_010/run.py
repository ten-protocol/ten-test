from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        # get the transaction count and deploy
        storage = Storage(self, web3, 100)
        tx_receipt = storage.deploy(network, account)

        # get the transaction count and interact
        tx = web3.eth.get_transaction(tx_receipt.transactionHash)
        self.assertTrue(tx_receipt.blockHash == tx.blockHash)
        self.assertTrue(tx_receipt.blockNumber == tx.blockNumber)
        self.assertTrue(tx_receipt.transactionHash == tx.hash)
        self.assertTrue(tx_receipt.transactionIndex == tx.transactionIndex)
