from pysys.constants import PASSED, FAILED
from collections import namedtuple
from web3.exceptions import TimeExhausted
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage

# expect 0=fail, 1=timeout, 2=success
Item = namedtuple("Item", "gas value nonce expect")

class TransactionFailed(Exception):
    pass

class Stack:
    def __init__(self): self.items = []
    def isEmpty(self): return self.items == []
    def append(self, item): self.items.append(item)
    def insert(self, item): return self.items.insert(0, item)
    def pop(self): return self.items.pop(0)
    def size(self): return len(self.items)

class PySysTest(GenericNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        contract = Storage(self, web3, 0)
        contract.deploy(network, account)

        # estimate gas required to call the add_once contract function
        estimate_gas = contract.contract.functions.store(1).estimate_gas()
        self.log.info("Estimate gas:    %d", estimate_gas)

        # these are the transactions to work through and their expectation on being mined or not
        stack = Stack()
        stack.append(Item(int(0.9 * estimate_gas), 1, None, 0))
        stack.append(Item(int(0.8 * estimate_gas), 2, None, 0))
        stack.append(Item(int(0.6 * estimate_gas), 3, None, 0))
        stack.append(Item(int(0.4 * estimate_gas), 4, None, 1))
        stack.append(Item(int(0.1 * estimate_gas), 5, None, 1))

        # process the stack of transactions
        last_value = 0
        while not stack.isEmpty():
            item = stack.pop()
            if last_value != item.value: self.log.info("")
            if item.nonce is None: item = Item(item.gas, item.value, self.nonce(web3, account), item.expect)

            self.log.info('Running for item: %s', item)
            try:
                self.log.info('Submitting the transaction value %d, gas %d, nonce %d', item.value, item.gas, item.nonce)
                self.submit(account, contract, web3, item)
                if item.expect == 2: self.addOutcome(PASSED)
                else: self.addOutcome(FAILED)
                self.log.info('Transaction was mined successfully')
            except TimeExhausted as e:
                self.log.error(e)
                if item.expect == 1: self.addOutcome(PASSED)
                else: self.addOutcome(FAILED)
                self.log.info('Inserting transaction to use same nonce but increase gas')
                stack.insert(Item(estimate_gas, item.value, item.nonce, 2))
            except TransactionFailed as e:
                self.log.error(e)
                if item.expect == 0: self.addOutcome(PASSED)
                else: self.addOutcome(FAILED)
            last_value = item.value

    def nonce(self, web3, account):
        return self.nonce_db.get_next_nonce(self, web3, account.address, self.env)

    def submit(self, account, contract, web3, item):
        build_tx = contract.contract.functions.store(1).build_transaction(
            {
                'nonce': item.nonce,
                'gasPrice': web3.eth.gas_price,
                'gas': item.gas,
                'chainId': web3.eth.chain_id
        })
        signed_tx = account.sign_transaction(build_tx)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=10)
        if tx_receipt.status == 1:
            self.nonce_db.update(account.address, self.env, item.nonce, 'CONFIRMED')
        else:
            try:
                web3.eth.call(build_tx, block_identifier=tx_receipt.blockNumber)
            except Exception as e:
                raise TransactionFailed(e)
            raise TransactionFailed('Failure processing transaction')
        return tx_receipt



