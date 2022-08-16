from ethsys.basetest import EthereumTest
from ethsys.contracts.error.error import Error
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1()

        error = Error(self, web3, 'foo')
        error.deploy(network, account)


