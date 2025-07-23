from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # user deploys contract and performs a transactions against it
        self.log.info('')
        self.log.info('User deploys contract and submits transactions against it')
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        tx_receipt = network.transact(self, web3, storage.contract.functions.store(78), account, storage.GAS_LIMIT)
        tx_block_hash = tx_receipt['blockHash'].hex()
        self.log.info(tx_receipt)
        self.log.info('Transaction made with reported block hash as %s', tx_block_hash)

        # this actually just returns the header of the latest batch
        block = self.scan_get_latest_batch()
        block_number1 = int(block['number'], 16)

        self.wait(2 * float(self.block_time))
        block = self.scan_get_latest_batch()
        block_number2 = int(block['number'], 16)

        self.log.info('First block %d, second block %d' % (block_number1, block_number2))
        self.assertTrue(block_number2 > block_number1, assertMessage='Latest block number should increase')
