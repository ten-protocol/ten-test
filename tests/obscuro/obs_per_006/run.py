from obscuro.test.contracts.storage import Storage
from obscuro.test.basetest import ObscuroNetworkTest


class PySysTest(ObscuroNetworkTest):
    ITERATIONS = 10
    CLIENTS = 5

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)






