import secrets
from web3 import Web3
from web3.exceptions import TimeExhausted
from pysys.constants import FAILED, PASSED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class TransactionFailed(Exception):
    pass


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network using an ephemeral account in-case anything gets messed up
        network = self.get_network_connection()
        private_key = secrets.token_hex(32)
        self.distribute_native(Web3().eth.account.from_key(private_key), 0.001)
        web3, account = network.connect(self, private_key=private_key, check_funds=False)

        contract = Storage(self, web3, 0)
        contract.deploy(network, account, persist_nonce=False)

        # estimate gas required to call the add_once contract function
        estimate_gas = contract.contract.functions.store(1).estimate_gas()
        self.log.info("Estimate gas:    %d", estimate_gas)

        # submit at the estimate with a nonce lower than it should be (should fail without being mined)
        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env, persist_nonce=False)
        use_nonce = nonce - 1
        self.log.info('Next nonce is %d, so using %d', nonce, use_nonce)
        self.submit(account, contract, web3, use_nonce, estimate_gas)

    def submit(self, account, contract, web3, nonce, gas_limit):
        build_tx = contract.contract.functions.store(1).build_transaction({
                'nonce': nonce,
                'gasPrice': web3.eth.gas_price,
                'gas': gas_limit,
                'chainId': web3.eth.chain_id })
        signed_tx = account.sign_transaction(build_tx)
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=30)
            self.addOutcome(FAILED, 'Transaction should not have been mined')

        except ValueError as e:
            self.log.error(e)
            self.addOutcome(PASSED, 'Transaction should be reject without being mined')

        except TimeExhausted as e:
            self.log.error(e)
            self.addOutcome(FAILED, 'Transaction should not have entered mempool')





