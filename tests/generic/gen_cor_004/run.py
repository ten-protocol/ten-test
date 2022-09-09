from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.storage import Storage
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1()
        self.log.info('Using account with address %s' % account.address)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # get the new block number
        block_number_deploy = network.get_block_number(web3)
        self.log.info('Block number is %d' % block_number_deploy)

        # get block by number
        block = network.get_block_by_number(web3, block_number_deploy)
        self.log.info('Block has number %s' % block.number)
        self.assertTrue(block.number == block_number_deploy)
