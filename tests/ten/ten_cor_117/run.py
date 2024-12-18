from pysys.constants import PASSED, FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.calldata import CallDataTwoPhase


class PySysTest(TenNetworkTest):
    GAS = '0'
    LIMIT = 5000

    def execute(self):
        # connect to the network (use an ephemeral account)
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)
        self.distribute_native(account, network.ETH_ALLOC)

        # deploy the contract
        calldata = CallDataTwoPhase(self, web3, Properties().L2PublicCallbacks)
        calldata.deploy(network, account)

        # transact (the first should be rejected so we just check later ones go through)
        self.transact(calldata, web3, account, limit=int(self.LIMIT), expect_pass=False)
        self.transact(calldata, web3, account, limit=1000)
        self.transact(calldata, web3, account, limit=500)

    def transact(self, calldata, web3, account, limit, expect_pass=True):
        self.log.info('Transacting with limit set to %d' % limit)

        # build the transaction
        large_array = [i for i in range(limit)]
        target = calldata.contract.functions.processLargeData(large_array)
        nonce = web3.eth.get_transaction_count(account.address)
        params = {'nonce': nonce,
                  'chainId': web3.eth.chain_id,
                  'gasPrice': web3.eth.gas_price,
                  'value': web3.to_wei(0.01, 'ether')}
        if self.GAS == 0:
            self.log.info('Estimating gas ...')
            params['gas'] = int(1.1 * target.estimate_gas(params))
        else:
            self.log.info('Using set gas limit of %d' % int(self.GAS))
            params['gas'] = int(self.GAS)
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

