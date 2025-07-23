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
        tx_hash = tx_receipt['transactionHash'].hex()
        tx_block_hash = tx_receipt['blockHash'].hex()
        self.log.info('Transaction made with reported block hash as %s', tx_block_hash)

        block = self.scan_get_batch(hash=tx_block_hash)
        self.assertTrue(tx_hash in block['TxHashes'], assertMessage='Tx hash should be in the list of block tx hashes')

