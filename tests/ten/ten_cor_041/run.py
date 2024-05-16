import secrets
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.expensive import ExpensiveContract


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network on the primary gateway and deploy the contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        contract = ExpensiveContract(self, web3)
        contract.deploy(network, account)

        # estimate the gas costs with increasing input
        steps = range(350, 370, 2)
        gas_price = web3.eth.gas_price
        gas_estimate = sum([contract.contract.functions.calculateFibonacci(x).estimate_gas() for x in steps])
        cost_estimate = gas_estimate*gas_price
        self.log.info('Total gas cost is %.9f ETH', web3.from_wei(cost_estimate, 'ether'))

        # create an ephemeral account and get their own reference to the contract
        web3, account = network.connect(self, private_key=secrets.token_hex(32), check_funds=False)
        contract = ExpensiveContract.clone(web3, account, contract)
        target = contract.contract.functions.calculateFibonacci
        self.distribute_native(account, web3.from_wei(1.2*cost_estimate, 'ether'))
        balance_before = web3.eth.get_balance(account.address)

        # build up pre-signed transactions with expected increasing gas costs
        self.log.info('Building and signing the transactions')
        txs = []
        nonce = 0
        for i in steps:
            tx = network.build_transaction(self, web3, target(i), nonce, account, contract.GAS_LIMIT, verbose=False)
            tx_sign = network.sign_transaction(self, tx, nonce, account, persist_nonce=False)
            txs.append((nonce, tx_sign))
            nonce = nonce + 1

        self.log.info('Sending  the transactions')
        tx_hashes = [network.send_transaction(self, web3, nonce, account, tx, persist_nonce=False) for nonce, tx in txs]

        tx_receipts = []
        for tx_hash in tx_hashes:
            tx_receipt = network.wait_for_transaction(self, web3, nonce, account, tx_hash, persist_nonce=False)
            self.assertTrue(tx_receipt.status == 1)
            tx_receipts.append(tx_receipt)

        # how much did it cost
        balance_after = web3.eth.get_balance(account.address)
        spent = (balance_before - balance_after)
        self.log.info('Total gas spent is %.9f ETH', web3.from_wei(spent, 'ether'))

        bn_first = tx_receipts[0]['blockNumber']
        bn_second = tx_receipts[-1]['blockNumber']
        self.log.info('Block number of first and last, %d %d', bn_first, bn_second)
        self.assertTrue(bn_second >= bn_first)
        if bn_first == bn_second: self.check(tx_receipts[-1])

    def check(self, tx_receipt):
        self.log.info('Transaction details;')
        tx_hash = tx_receipt['transactionHash'].hex()
        block_num = tx_receipt['blockNumber']
        block_hash = tx_receipt['blockHash'].hex()
        self.log.info('  Block Num:  %s ', block_num)
        self.log.info('  Block Hash: %s ', block_hash)
        self.log.info('  TX Hash:    %s ', tx_hash)

        batch = self.scan_get_batch_for_transaction(tx_hash)
        if batch is not None:
            batch_txns = batch['TxHashes']
            self.log.info('Number of transactions in the batch are %d', len(batch_txns))
            self.assertTrue(len(batch_txns) == 10)