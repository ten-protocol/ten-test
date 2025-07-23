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
        tx_block_number = tx_receipt['blockNumber']
        self.log.info('Transaction made with reported block number as %s', tx_block_number)
        tx_block_hash = tx_receipt['blockHash'].hex()
        self.log.info('Transaction made with reported block hash as %s', tx_block_hash)

        block_by_height = self.scan_get_batch_by_height(height=tx_block_number)
        self.log.info('Block by height: %s', block_by_height)
        block_by_hash = self.scan_get_batch(hash=tx_block_hash)
        self.log.info('Block by hash: %s', block_by_hash)


