from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.fibonacci import Fibonacci


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        contract = Fibonacci(self, web3)
        contract.deploy(network, account)

        nonce = None
        tx_hash = None
        for i in range(200,300,25):
            target = contract.contract.functions.calculateFibonacci(i)
            #gas_estimate = target.estimate_gas()
            #self.log.info('Gas estimate, cost is %d WEI', gas_estimate)
            nonce = network.get_next_nonce(self, web3, account, True)
            tx = network.build_transaction(self, web3, target, nonce, contract.GAS_LIMIT)
            tx_sign = network.sign_transaction(self, tx, nonce, account, True)
            tx_hash = network.send_transaction(self, web3, nonce, account, tx_sign, True)
            self.log.info('Transaction set with hash tx_hash %s', tx_hash.hex())

        tx_receipt = network.wait_for_transaction(self, web3, nonce, account, tx_hash, True)
        self.check(tx_receipt)

    def check(self, tx_receipt):
        self.log.info('Transaction details;')
        tx_hash = tx_receipt['transactionHash'].hex()
        block_num = tx_receipt['blockNumber']
        block_hash = tx_receipt['blockHash'].hex()
        self.log.info('  Block Num:  %s ', block_num)
        self.log.info('  Block Hash: %s ', block_hash)
        self.log.info('  TX Hash:    %s ', tx_hash)

        batch = self.get_batch_for_transaction(tx_hash)
        if batch is not None:
            batch_number = batch['Header']['number']
            batch_txns = batch['TxHashes']
            self.log.info(batch)