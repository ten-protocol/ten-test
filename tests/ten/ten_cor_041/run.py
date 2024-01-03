import secrets
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.expensive import ExpensiveContract


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)

        contract_deploy = ExpensiveContract(self, web3_deploy)
        contract_deploy.deploy(network, account_deploy)

        pk = secrets.token_hex(32)
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        contract = ExpensiveContract.clone(web3, account, contract_deploy)
        self.distribute_native(account, 0.01)

        estimate = 0
        nonce = 0
        txs = []
        self.log.info('Calculating total gas estimate')
        for i in range(350, 370, 2):
            target = contract.contract.functions.calculateFibonacci(i)
            estimate = estimate + target.estimate_gas()
            tx = network.build_transaction(self, web3, target, nonce, account, contract.deploy.GAS_LIMIT)
            tx_sign = network.sign_transaction(self, tx, nonce, account, True)
            txs.append((nonce, tx_sign))
            nonce = nonce + 1
        self.log.info('Total gas estimate is %d WEI, %.9f ETH', estimate, web3.from_wei(estimate, 'ether'))

        tx_hash = None
        for nonce, tx_sign in txs: tx_hash = network.send_transaction(self, web3, nonce, account, tx_sign, True)
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

        batch = self.tenscan_get_batch_for_transaction(tx_hash)
        if batch is not None:
            batch_txns = batch['TxHashes']
            self.log.info('Number of transactions in the batch are %d', len(batch_txns))
            self.assertTrue(len(batch_txns) > 0)