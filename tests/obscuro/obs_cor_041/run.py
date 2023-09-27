from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.fibonacci import Fibonacci

class PySysTest(GenericNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        contract = Fibonacci(self, web3)
        contract.deploy(network, account)
