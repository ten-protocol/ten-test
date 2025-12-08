from web3.exceptions import TimeExhausted
from pysys.constants import PASSED, FAILED
from ten.test.utils.exceptions import *
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network, deploy contract and estimate gas
        network = self.get_network_connection()
        web3_1, account_1 = network.connect_account1(self)

        contract_1 = Storage(self, web3_1, 0)
        contract_1.deploy(network, account_1)
        estimate_gas = contract_1.contract.functions.store(1).estimate_gas()

        # connect an ephemeral account, grab a reference to the contract with it's details and give it
        # enough funds to cover the expected cost
        private_key = self.get_ephemeral_pk()
        web3, account = network.connect(self, private_key=private_key, check_funds=False)
        contract = Storage.clone(web3, account, contract_1)

        gas_price = web3.eth.gas_price
        funds = estimate_gas * gas_price
        self.distribute_native(account, web3.from_wei(funds, 'ether'))
        self.log.info('Balance of account is now %d' % web3.eth.get_balance(account.address))

        # submit with double the gas price - expect this to error
        self.log.info('Submitting transaction with gas_price of %d', 2*gas_price)
        try:
            self.submit(account, contract.contract.functions.store(1), web3, 0, 2*gas_price, estimate_gas)
            self.addOutcome(FAILED, 'Transaction error was not received as expected')
        except TransactionError:
            self.addOutcome(PASSED, 'Transaction error received as expected')

        # submit with the actual gas price - expect this to pass
        self.log.info('Submitting transaction with gas_price of %d', gas_price)
        try:
            self.submit(account, contract.contract.functions.store(1), web3, 0, gas_price, estimate_gas)
            self.addOutcome(PASSED, 'Transaction error was successful as expected')
        except TransactionError:
            self.addOutcome(FAILED, 'Transaction error was not successful as expected')

        self.log.info('Balance of account is now %d' % web3.eth.get_balance(account.address))


    def submit(self, account, target, web3, nonce, gas_price, gas_limit):
        build_tx = target.build_transaction({
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'chainId': web3.eth.chain_id})
        signed_tx = account.sign_transaction(build_tx)
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=30)
            if tx_receipt.status == 1:
                return tx_receipt
            else:
                try:
                    web3.eth.call(build_tx, block_identifier=tx_receipt.blockNumber)
                except Exception as e:
                    self.log.error('Replay call: %s', e)
                raise TransactionFailed('Transaction status shows failure')

        except ValueError as e:
            self.log.error(e.args[0]['message'])
            raise TransactionError('Transaction rejected by the mem pool')

        except TimeExhausted as e:
            self.log.error(e.args[0]['message'])
            raise TransactionTimeOut('Transaction timed out waiting for receipt')

