from ethsys.basetest import EthereumTest
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1()
        self.log.info('Using account with address %s' % account.address)

        # get gas price
        gas_price = network.gas_price(web3)
        self.log.info('Gas price is %s' % gas_price)
        self.assertTrue(gas_price >= 0)
