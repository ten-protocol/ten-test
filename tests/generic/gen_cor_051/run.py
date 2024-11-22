import re
from pysys.constants import PASSED, FAILED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.error import Error


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network and deploy the contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self, web_socket=True)

        error = Error(self, web3)
        error.deploy(network, account)

        # transact successfully
        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env)
        self.submit(account, error.contract.functions.set_key("new"), web3, nonce)

        # force a require
        nonce = self.nonce_db.get_next_nonce(self, web3, account.address, self.env)
        self.submit(account, error.contract.functions.set_key(""), web3, nonce)

    def submit(self, account, target, web3, nonce, expect_success=True):
        build_tx = target.build_transaction({
            'nonce': nonce,
            'gasPrice': web3.eth.gas_price,
            'gas': 10*21000,                    # hard code the gas as an estimate will fail
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
