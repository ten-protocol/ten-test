import secrets
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.fibonacci import Fibonacci


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)

        contract = Fibonacci(self, web3_deploy)
        contract.deploy(network, account_deploy)

        pk = secrets.token_hex(32)
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, 0.01)

        nonce = 0
        txs = []
        for i in range(200, 300, 25):
            target = contract.contract.functions.calculateFibonacci(i)
            tx = network.build_transaction(self, web3, target, nonce, contract.GAS_LIMIT)
            tx_sign = network.sign_transaction(self, tx, nonce, account, True)
            txs.append((nonce, tx_sign))
            nonce = nonce + 1

        tx_hash = None
        for nonce, tx_sign in txs:
            tx_hash = network.send_transaction(self, web3, nonce, account, tx_sign, True)

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