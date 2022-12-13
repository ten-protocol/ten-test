from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)
        self.log.info('Using account with address %s' % account.address)

        # get gas price
        gas_price = web3.eth.gas_price
        self.log.info('Gas price is %s' % gas_price)
        self.assertTrue(gas_price >= 0)
