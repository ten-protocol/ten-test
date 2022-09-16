from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.storage import Storage
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
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

