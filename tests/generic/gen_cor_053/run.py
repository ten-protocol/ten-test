from pysys.constants import FAILED, PASSED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class TransactionFailed(Exception):
    pass


class PySysTest(GenericNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        contract = Storage(self, web3, 0)
        contract.deploy(network, account)

        # estimate gas required to call the add_once contract function
        estimate_gas = contract.contract.functions.store(1).estimate_gas()
        self.log.info("Estimate gas:    %d", estimate_gas)

        # submit at the estimate and then from the transaction work out the intrinsic gas
        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env, persist_nonce=False)
        use_nonce = nonce - 1
        self.log.info('Next nonce is %d, so using %d', nonce, use_nonce)
        self.submit(account, contract, web3, use_nonce, estimate_gas)

    def submit(self, account, contract, web3, nonce, gas_limit):
        tx_receipt = None
        build_tx = contract.contract.functions.store(1).build_transaction(
            {
                'nonce': nonce,
                'gasPrice': web3.eth.gas_price,
                'gas': gas_limit,
                'chainId': web3.eth.chain_id
            })
        signed_tx = account.sign_transaction(build_tx)
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=30)
            self.addOutcome(FAILED, 'Expect ValueError exception to be raised')

        except ValueError as e:
            self.log.error(e)
            self.addOutcome(PASSED, 'ValueError exception raised')

        finally:
            return tx_receipt


