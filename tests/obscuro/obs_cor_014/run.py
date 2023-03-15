from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 0)
        tx_receipt = storage.deploy(network, account)
        tx_hash = tx_receipt['transactionHash'].hex()

        # get the rollup
        batch = self.get_batch_for_transaction(tx_hash)
        self.log.info(batch)
        l1_proof = batch['Header']['L1Proof']
        self.log.info(l1_proof)

