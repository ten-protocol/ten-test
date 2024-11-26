import secrets
from web3 import Web3
from hexbytes import HexBytes
from web3.exceptions import TimeExhausted
from pysys.constants import PASSED, FAILED
from ten.test.utils.exceptions import *
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network using an ephemeral account in-case anything gets messed up
        # deploy the storage contract but don't persist the nonce
        network = self.get_network_connection()
        private_key = secrets.token_hex(32)
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC_EPHEMERAL)
        web3, account = network.connect(self, private_key=private_key, check_funds=False)

        contract = Storage(self, web3, 0)
        contract.deploy(network, account, persist_nonce=False)

        # estimate gas required to call the store contract function
        target = contract.contract.functions.store(1)
        estimate_gas = target.estimate_gas()

        # submit at the estimate and then from the transaction work out the intrinsic gas
        self.log.info('Submitting transaction with gas_limit of %d', estimate_gas)
        tx_receipt = self.submit(account, target, web3, 1, estimate_gas)
        intrinsic_gas = self.calculate_intrinsic_gas(web3, tx_receipt.transactionHash)

        # submit at lower than the intrinsic gas - expect this to error
        gas_limit = int(0.9*intrinsic_gas)
        self.log.info('Submitting transaction with gas_limit of %d', gas_limit)
        try:
            self.submit(account, target, web3, 2, gas_limit)
            self.addOutcome(FAILED, 'Transaction error was not received as expected')
        except TransactionError:
            self.addOutcome(PASSED, 'Transaction error received as expected')

        # return remaining funds
        self.drain_native(web3, account, network)

    def submit(self, account, target, web3, nonce, gas_limit):
        build_tx = target.build_transaction({
                'nonce': nonce,
                'gasPrice': web3.eth.gas_price,
                'gas': gas_limit,
                'chainId': web3.eth.chain_id })
        signed_tx = account.sign_transaction(build_tx)
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=30)
            if tx_receipt.status == 1: return tx_receipt
            else:
                try: web3.eth.call(build_tx, block_identifier=tx_receipt.blockNumber)
                except Exception as e: self.log.error('Replay call: %s', e)
                raise TransactionFailed('Transaction status shows failure')

        except ValueError as e:
            self.log.error(e.args[0]['message'])
            raise TransactionError('Transaction rejected by the mem pool')

        except TimeExhausted as e:
            self.log.error(e.args[0]['message'])
            raise TransactionTimeOut('Transaction timed out waiting for receipt')

    def calculate_intrinsic_gas(self, web3, tx_hash):
        tx = web3.eth.get_transaction(tx_hash)
        hex_data = HexBytes(tx['input'])
        zero_count = sum(1 for byte in hex_data if byte == 0)
        non_zero_count = sum(1 for byte in hex_data if byte != 0)
        intrinsic_gas = 21000 + (16*non_zero_count) + (4*zero_count)
        self.log.info('Intrinsic gas is calculated to be %d', intrinsic_gas)
        return intrinsic_gas
