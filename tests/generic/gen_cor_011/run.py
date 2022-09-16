from ethsys.basetest import EthereumTest
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=True)
        self.log.info('Using account with address %s' % account.address)

        # get the chain id
        chain_id = web3.eth.chainId
        self.log.info('Chain id is %d' % chain_id)
        self.assertTrue(chain_id == network.chain_id())
