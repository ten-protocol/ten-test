from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)
        self.log.info('Using account with address %s' % account.address)

        # get the block number
        block_number_initial = web3.eth.get_block_number()
        self.log.info('Block number is %d' % block_number_initial)
        self.assertTrue(block_number_initial >= 0)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # get the new block number
        block_number_deploy = web3.eth.get_block_number()
        self.log.info('Block number is %d' % block_number_deploy)
        self.assertTrue(block_number_deploy > block_number_initial)
