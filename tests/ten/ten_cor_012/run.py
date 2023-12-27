from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 0)
        tx_receipt = storage.deploy(network, account)
        self.wait(float(self.block_time)*1.1)
        self.check(tx_receipt)

        for i in range(0,4):
            tx_receipt = network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)
            self.wait(float(self.block_time)*1.1)
            self.check(tx_receipt)

    def check(self, tx_receipt):
        self.log.info('Transaction details;')
        tx_hash = tx_receipt['transactionHash'].hex()
        block_num = tx_receipt['blockNumber']
        block_hash = tx_receipt['blockHash'].hex()
        self.log.info('  Block Num:  %s ', block_num)
        self.log.info('  Block Hash: %s ', block_hash)
        self.log.info('  TX Hash:    %s ', tx_hash)

        batch = self.tenscan_get_batch_for_transaction(tx_hash)
        if batch is not None:
            batch_number = int(batch['Header']['number'], 16)
            batch_txns = batch['TxHashes']

            self.log.info('Batch details;')
            self.log.info('  Batch Num:  %s ', batch_number)
            self.log.info('  Tx in list: %s', tx_hash in batch_txns)

            self.assertTrue(batch_number==block_num)
            self.assertTrue((tx_hash in batch_txns))

        self.log.info('')