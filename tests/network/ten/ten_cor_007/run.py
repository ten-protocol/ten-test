from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 0)
        tx_receipt = storage.deploy(network, account)
        tx_hash = tx_receipt['transactionHash'].hex()

        # get the batch for transaction and from that the l1 proof
        batch = self.scan_get_batch_for_transaction(tx_hash)
        l1_proof = batch['header']['l1Proof']

        # if we get this far we'll treat it as a pass
        self.addOutcome(PASSED)


