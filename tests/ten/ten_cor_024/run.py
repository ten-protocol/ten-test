import time, rlp
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.helpers.merkle_tree import MerkleTreeHelper
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 4000000000000000
        gas_attempts = 12 if self.is_local_ten() else 480 # 1min on a local, 40min otherwise

        # create the bridge user
        accnt = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')
        l1_before = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)
        l2_before = accnt.l2.web3.eth.get_balance(accnt.l2.account.address)

        # send funds from the L2 to the L1
        self.log.info('Send native from L2 to L1')
        self.log.info('Fees to send are %d' % accnt.l2.send_native_fees())
        tx_receipt, value_transfer = accnt.l2.send_native(accnt.l1.account.address, transfer, dump_file='send_native.tx')
        l2_cost = int(tx_receipt.gasUsed) * accnt.l2.web3.eth.gas_price

        # calculate tree ourselves and assert on values
        mh = MerkleTreeHelper.create(self)
        block, decoded = mh.dump_tree(accnt.l2.web3, tx_receipt, 'xchain_tree.log')
        msg, msg_hash = mh.process_transfer(value_transfer)
        root, proof = mh.get_proof('xchain_tree.log', 'v,%s' % msg_hash)
        self.log.info('  value_transfer:        %s', msg)
        self.log.info('  value_transfer_hash:   %s', msg_hash)
        self.log.info('  cross_chain:           %s', decoded)
        self.log.info('  merkle_root:           %s', block.crossChainTreeHash)
        self.log.info('  calculated root:       %s', root)
        self.log.info('  calculated proof:      %s', proof)
        self.assertTrue(msg_hash in [x[1] for x in decoded],
                        assertMessage='Value transfer has should be in the xchain tree')
        self.assertTrue(root == block.crossChainTreeHash,
                        assertMessage='Calculated root should be same as the crossChainTreeHash')

        # get the root and proof of inclusion from the node
        self.log.info('Request proof and root from the node')
        root, proof = None, None
        start = time.time()
        while root is None:
            proof, root = self.ten_get_xchain_proof('v', msg_hash)
            if root is not None: break
            if time.time() - start > 60:
                raise TimeoutError('Timed out waiting for message to be verified')
            time.sleep(2.0)
        proof = rlp.decode(bytes.fromhex(proof[2:]))

        self.log.info('Received proof and root from the node')
        self.log.info('  returned root:         %s', root)
        self.log.info('  returned proof:        %s', [p.hex() for p in proof])
        self.assertTrue(root == block.crossChainTreeHash,
                        assertMessage='Returned root should be same as the crossChainTreeHash')

        # release the funds from the L1 and check the balances
        start_time = time.perf_counter_ns()
        tx_receipt = accnt.l1.release_funds(msg, proof, root, gas_attempts=gas_attempts)
        end_time = time.perf_counter_ns()
        self.log.info('Total time waiting for the gas estimate to pass: %.1f secs', (end_time-start_time)/1e9)

        l1_cost = int(tx_receipt.gasUsed) * int(tx_receipt.effectiveGasPrice)
        l1_after = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)
        l2_after = accnt.l2.web3.eth.get_balance(accnt.l2.account.address)
        self.log.info('  l1_balance before:     %s', l1_before)
        self.log.info('  l2_balance before:     %s', l2_before)
        self.log.info('  l1_balance after:      %s', l1_after)
        self.log.info('  l2_balance after:      %s', l2_after)
        self.log.info('  l1_cost:               %s', l1_cost)
        self.log.info('  l2_cost:               %s', l2_cost)
        self.log.info('  l1_delta (inc):        %s', l1_after-l1_before)
        self.log.info('  l1_delta (with cost):  %s', l1_after-l1_before+l1_cost)
        self.log.info('  l2_delta (dec):        %s', l2_before-l2_after)
        self.log.info('  l2_delta (with cost):  %s', l2_before-l2_after-l2_cost)
        self.assertTrue(l1_after-l1_before+l1_cost == transfer,
                        assertMessage='L1 balance should increase by transfer amount plus gas for releasing')
