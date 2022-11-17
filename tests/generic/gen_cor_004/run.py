from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)
        self.log.info('Using account with address %s' % account.address)

        storage = Storage(self, web3, 100)
        tx_receipt = storage.deploy(network, account)

        # get the new block number
        block_number_deploy = tx_receipt.blockNumber
        self.log.info('Block number is %d' % block_number_deploy)

        # get block by number
        block = web3.eth.get_block(block_number_deploy)
        self.log.info('Block has number %s' % block.number)
        self.assertTrue(block.number == block_number_deploy)
