from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 0)
        tx_receipt = storage.deploy(network, account)

        # get the transaction
        tx = web3.eth.get_transaction(tx_receipt.transactionHash)
        l1_proof = tx.L1Proof
        self.log.info('L1 proof hash is %s' % l1_proof)

