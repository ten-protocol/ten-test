import threading
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account2(self)
        self.log.info('Using account with address %s' % account.address)

        # get the block number
        block_number_initial = web3.eth.get_block_number()
        self.log.info('Block number is %d' % block_number_initial)
        self.assertTrue(block_number_initial >= 0)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # wait a couple of block times
        self.wait(2.0*float(self.block_time))

        # get the new block number
        block_number_deploy = web3.eth.get_block_number()
        self.log.info('Block number is %d' % block_number_deploy)
        self.assertTrue(block_number_deploy > block_number_initial)
