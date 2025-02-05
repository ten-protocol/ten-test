from pysys.constants import FAILED, PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.calldata import CallData


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network (use an ephemeral account)
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)
        self.distribute_native(account, network.ETH_ALLOC)

        # deploy the contract
        calldata = CallData(self, web3)
        calldata.deploy(network, account)

        # transact (the first should be rejected so we just check later ones go through)
        self.transact(calldata, web3, account, limit=5000, expect_pass=False)
        self.transact(calldata, web3, account, limit=1000)
        self.transact(calldata, web3, account, limit=500)

    def transact(self, calldata, web3, account, limit, expect_pass=True):
        # build the transaction
        large_array = [i for i in range(limit)]
        target = calldata.contract.functions.processLargeData(large_array)
        nonce = web3.eth.get_transaction_count(account.address)
        params = {'nonce': nonce,
                  'chainId': web3.eth.chain_id,
                  'gasPrice': web3.eth.gas_price}
        params['gas'] = int(1.1 * target.estimate_gas(params))
        build_tx = target.build_transaction(params)

        # sign, send and wait
        try:
            signed_tx = account.sign_transaction(build_tx)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            if tx_receipt.status == 1:
                self.log.info('Transaction confirmed')
                self.log.info('Expected sum:     %d' % sum(large_array))
                self.log.info('Call shows value: %d', calldata.contract.functions.getLastSum().call())
                self.assertTrue(calldata.contract.functions.getLastSum().call() == sum(large_array))
            else:
                self.log.error('Transaction failed')
                if expect_pass: self.addOutcome(FAILED,outcomeReason='Expected tx to succeed')
        except Exception as e:
            self.log.error('Error %s' % e)
            if expect_pass: self.addOutcome(FAILED,outcomeReason='Expected tx to succeed')
            else: self.addOutcome(PASSED,outcomeReason='Expected tx to fail')
