import json
from pysys.constants import FAILED, PASSED
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage import Storage


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # first wallet extension, two accounts, account 1 transacts
        # deploy contract, transact as account 1, account 2 gets the transaction
        network_1 = self.get_network_connection(name='network_1')
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_1.connect_account2(self)

        storage = Storage(self, web3_1, 100)
        storage.deploy(network_1, account_1)
        tx_receipt = network_1.transact(self, web3_1, storage.contract.functions.store(128), account_1, storage.GAS_LIMIT)

        tx_hash = tx_receipt.transactionHash
        block_number = tx_receipt.blockNumber

        self.log.info('Getting transaction for account 2 (through network connection 1)')
        tx_rec = web3_2.eth.get_transaction_receipt(tx_hash)
        with open(storage.abi_path) as f: contract = web3_2.eth.contract(address=storage.address, abi=json.load(f))
        tx_log = contract.events.Stored().processReceipt(tx_rec)[0]
        args_value = tx_log['args']['value']
        self.log.info('Transaction log shows value %d', args_value)
        self.assertTrue(args_value == 128)

        # second wallet extension, account 3 tries to get the transaction receipt
        # but also just requests all event logs for the Stored event
        network_2 = self.get_network_connection(name='network_2')
        web3_3, account_3 = network_2.connect_account3(self)

        self.log.info('Getting transaction for account 3 (through network connection 2)')
        try:
            web3_3.eth.get_transaction_receipt(tx_hash)
            self.addOutcome(FAILED)
        except:
            self.log.warn('It is not possible to get someone else transaction receipt')
            self.addOutcome(PASSED)

        self.log.info('Attempting to get the past events from the contract instance')
        with open(storage.abi_path) as f: contract = web3_3.eth.contract(address=storage.address, abi=json.load(f))
        for event in contract.events.Stored().getLogs(fromBlock=block_number):
            self.log.info('Stored value = %s', event['args']['value'])