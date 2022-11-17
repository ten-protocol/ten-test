from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        block_time = Properties().block_time_secs(self.env)

        network = Obscuro
        web3, account = network.connect_account1(self)

        storage = Storage(self, web3, 0)
        tx_receipt = storage.deploy(network, account)
        self.wait(float(block_time)*1.1)
        self.check(tx_receipt)

        for i in range(0,4):
            tx_receipt = network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS)
            self.wait(float(block_time)*1.1)
            self.check(tx_receipt)

    def check(self, tx_receipt):
        self.log.info('Transaction details;')
        tx_hash = tx_receipt['transactionHash'].hex()
        block_num = tx_receipt['blockNumber']
        block_hash = tx_receipt['blockHash'].hex()
        self.log.info('  Block Num:  %s ' % block_num)
        self.log.info('  Block Hash: %s ' % block_hash)
        self.log.info('  TX Hash:    %s ' % tx_hash)

        rollup = self.get_rollup_for_transaction(tx_hash)
        if rollup is not None:
            rollup_number = rollup['Header']['Number']
            rollup_txns = rollup['TxHashes']

            self.log.info('Rollup details;')
            self.log.info('  Rollup Num:  %s ' % rollup_number)
            self.log.info('  Tx in list: %s' % (tx_hash in rollup_txns))

            self.assertTrue(rollup_number==block_num)
            self.assertTrue((tx_hash in rollup_txns))

        self.log.info('')