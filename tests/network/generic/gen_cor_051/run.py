import re
from pysys.constants import PASSED, FAILED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.error import Error


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network and deploy the contract
        network = self.get_network_connection()
        private_key = self.get_ephemeral_pk()
        web3, account = network.connect(self, private_key=private_key, web_socket=True)

        error = Error(self, web3)
        error.deploy(network, account)

        # transact successfully
        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env)
        estimate = error.contract.functions.set_key_with_require("new").estimate_gas()
        self.log.info('Estimating gas to be %d', estimate)
        self.submit(account, error.contract.functions.set_key_with_require("new"), web3, nonce, estimate)

        # force a require
        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env)
        self.submit(account, error.contract.functions.set_key_with_require(""), web3, nonce, estimate, expect_success=False)

    def submit(self, account, target, web3, nonce, estimate, expect_success=True):
        build_tx = target.build_transaction({
            'nonce': nonce,
            'gasPrice': web3.eth.gas_price,
            'gas': estimate,
            'chainId': web3.eth.chain_id
        })
        signed_tx = account.sign_transaction(build_tx)
        self.nonce_db.update(account.address, self.env, nonce, 'SIGNED')

        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.nonce_db.update(account.address, self.env, nonce, 'SENT')

        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash.hex(), timeout=30)
        if tx_receipt.status == 1:
            self.log.info('Transaction successful')
            self.nonce_db.update(account.address, self.env, nonce, 'CONFIRMED')
            self.addOutcome(PASSED if expect_success else FAILED, 'Transaction should pass')
        else:
            self.log.info('Transaction failed')
            self.nonce_db.update(account.address, self.env, nonce, 'FAILED')
            try:
                web3.eth.call(build_tx, block_identifier=tx_receipt.blockNumber)
            except Exception as e:
                self.addOutcome(FAILED if expect_success else PASSED, 'Transaction should fail')
                self.log.error('Replay call: %s', e)
                regex = re.compile('.*New key cannot be empty', re.M)
                self.assertTrue(regex.search(e.args[0]) is not None)
        return tx_receipt
