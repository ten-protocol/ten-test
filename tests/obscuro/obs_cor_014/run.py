from ten.test.basetest import ObscuroNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 0)
        tx_receipt = storage.deploy(network, account)
        tx_hash = tx_receipt['transactionHash'].hex()

        # get the batch for transaction and from that the l1 proof
        batch = self.get_batch_for_transaction(tx_hash)
        l1_proof = batch['Header']['l1Proof']

