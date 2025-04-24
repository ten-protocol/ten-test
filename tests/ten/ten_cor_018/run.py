import traceback
from pysys.constants import PASSED, FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network (use an ephemeral account)
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)
        self.distribute_native(account, network.ETH_ALLOC_EPHEMERAL)

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        target = storage.contract.functions.store(100)
        params = {'from':account.address, 'chainId': web3.eth.chain_id, 'gasPrice': web3.eth.gas_price}
        estimate = target.estimate_gas(params)

        # transact (the first should be rejected so we just check later ones go through)
        self.transact(storage, web3, account, 101, estimate, chainId=web3.eth.chain_id, expect_pass=True)
        self.transact(storage, web3, account, 102, estimate, chainId=200, expect_pass=False)

    def transact(self, storage, web3, account, value, estimate, chainId, expect_pass=True):
        target = storage.contract.functions.store(value)
        nonce = web3.eth.get_transaction_count(account.address)
        params = {'from':account.address, 'nonce': nonce, 'chainId': chainId,
                  'gasPrice': web3.eth.gas_price, 'gas':estimate}
        build_tx = target.build_transaction(params)

        try:
            signed_tx = account.sign_transaction(build_tx)
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
            self.log.error('Transaction failed')
            self.log.error('Stack trace:' + traceback.format_exc())
            if expect_pass:
                self.addOutcome(FAILED, outcomeReason='Expected tx to succeed')
            else:
                self.addOutcome(PASSED, outcomeReason='Expected tx to fail')
