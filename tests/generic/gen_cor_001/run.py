import threading
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # get the chain id
        chain_id = web3.eth.chain_id
        self.log.info('Chain id is %d', chain_id)
        self.assertTrue(chain_id == network.chain_id())
