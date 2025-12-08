from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 100)
        tx_receipt = storage.deploy(network, account)

        # get the new block number
        block_number_deploy = tx_receipt.blockNumber
        self.log.info('Block number is %d', block_number_deploy)

        # get block by number
        block = web3.eth.get_block(block_number_deploy)
        self.log.info('Block has number %s', block.number)
        self.assertTrue(block.number == block_number_deploy)

        # get block by hash
        block = web3.eth.get_block(block.parentHash)
        self.log.info('Block has number %s', block.number)
        self.assertTrue(block.number == block_number_deploy - 1)
