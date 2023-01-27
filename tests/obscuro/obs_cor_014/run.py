from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        block_time = Properties().block_time_secs(self.env)

        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 0)
        tx_receipt = storage.deploy(network, account)
        self.wait(float(block_time) * 1.1)
        self.check(tx_receipt)
