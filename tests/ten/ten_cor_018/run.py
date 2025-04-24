from pysys.constants import PASSED, FAILED
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the l1 and l2 networks (we will only transact on the l2)
        l1 = self.get_l1_network_connection()
        l2 = self.get_network_connection(name='local')
        _, account_to = l2.connect_account1(self, check_funds=False)

        pk = self.get_ephemeral_pk()
        web3_l1, account_l1 = l1.connect(self, private_key=pk, check_funds=False)
        web3_l2, account_l2 = l2.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account_l2, l2.ETH_ALLOC_EPHEMERAL)

        # transact using the tx signed from the l2 details
        tx, signed_tx = self.get_signed_transaction(web3_l2, account_l2, account_to.address, 10, l2.chain_id())
        self.send_signed_transaction(web3_l2, tx, signed_tx, expect_pass=True)

        # transact using the tx signed from the l2 details but with a bogus chain ID
        tx, signed_tx = self.get_signed_transaction(web3_l2, account_l2, account_to.address, 10, 123456)
        self.send_signed_transaction(web3_l2, tx, signed_tx, expect_pass=False)
        self.assertGrep(file='wallet_local_logs',
                        expr='invalid sender: invalid chain id for signer: have %d want %d' % (123456, l2.chain_id()))

        # transact using the tx signed from the l1 details and signed on the l1
        tx, signed_tx = self.get_signed_transaction(web3_l1, account_l1, account_to.address, 10, l1.chain_id())
        self.send_signed_transaction(web3_l2, tx, signed_tx, expect_pass=False)
        self.assertGrep(file='wallet_local_logs',
                        expr='invalid sender: invalid chain id for signer: have %d want %d' % (l1.chain_id(), l2.chain_id()))

    def get_signed_transaction(self, web3, account, address, amount, chain_id):
        self.log.info('Creating signed transaction')
        nonce = web3.eth.get_transaction_count(account.address)
        tx = {'nonce': nonce, 'from': account.address, 'to': address, 'value': amount,
              'chainId': chain_id, 'gasPrice': web3.eth.gas_price, 'gas': 42000}
        return tx, account.sign_transaction(tx)

    def send_signed_transaction(self, web3, build_tx, signed_tx, expect_pass=True):
        self.log.info('Sending signed transaction')
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')
            else:
                self.log.error('Transaction failed')
                web3.eth.call(build_tx, block_identifier=tx_receipt.blockNumber)
                self.log.warn('Replaying the transaction did not throw an error')
                if expect_pass: self.addOutcome(FAILED, outcomeReason='Expected tx to succeed')
        except Exception as e:
            self.log.warn('Transaction failed: %s' % e)
            if expect_pass:
                self.addOutcome(FAILED, outcomeReason='Expected tx to succeed')
            else:
                self.addOutcome(PASSED, outcomeReason='Expected tx to fail')
