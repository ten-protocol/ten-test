from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account2(self)

        # get the gas price for reference
        gas_price = web3.eth.gas_price
        self.log.info('Gas price is %d', gas_price)

        # get the block number and deploy contract
        block_number_initial = web3.eth.get_block_number()
        self.log.info('Block number is %d', block_number_initial)
        self.assertTrue(block_number_initial >= 0)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # wait a couple of block times
        self.wait(5.0*float(self.block_time))

        # get the new block number
        block_number_deploy = web3.eth.get_block_number()
        self.log.info('Block number is %d', block_number_deploy)
        self.assertTrue(block_number_deploy > block_number_initial)
