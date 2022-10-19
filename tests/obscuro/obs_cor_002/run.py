from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.contracts.relevancy.relevancy import Relevancy
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        storage = Relevancy(self, web3)
        storage.deploy(network, account)
