import time
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.helpers.merkle_tree import MerkleTreeHelper
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):
    GAS_ATTEMPTS = 480  # 480 * 5 == 40 mins wait for the L2 to L1 rollup xchain msg to be received

    def execute(self):
        props = Properties()
        transfer = 4000000000000000

        # create the bridge user
        accnt = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')
        l1_before = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)
        l2_before = accnt.l2.web3.eth.get_balance(accnt.l2.account.address)

        # send funds from the L2 to the L1
        self.log.info('Send native from L2 to L1')
        tx_receipt, value_transfer = accnt.l2.send_native(accnt.l1.account.address, transfer, dump_file='send_native.tx')
        l2_cost = int(tx_receipt.gasUsed) * accnt.l2.web3.eth.gas_price

        # dump the tree, log out details and assert the transfer is in the tree
        mh = MerkleTreeHelper.create(self)
        block, decoded = mh.dump_tree(accnt.l2.web3, tx_receipt, 'cross_train_tree.log')
        msg, msg_hash = mh.process_transfer(value_transfer)
        self.log.info('  value_transfer:        %s', msg)
        self.log.info('  value_transfer_hash:   %s', msg_hash)
        self.log.info('  cross_chain:           %s', decoded)
        self.log.info('  merkle_root:           %s', block.crossChainTreeHash)
        self.assertTrue(msg_hash in [x[1] for x in decoded],
                        assertMessage='Value transfer has should be in the xchain tree')

        # from the dump, get the root and proof of inclusion and assert same root as in the block header
        root, proof = mh.get_proof('cross_train_tree.log', 'v,%s' % msg_hash)
        self.log.info('  calculated root:      %s', root)
        self.log.info('  calculated proof:     %s', proof)
        self.assertTrue(block.crossChainTreeHash == root,
                        assertMessage='Calculated merkle root should be same as the block header')

        # release the funds from the L1 and check the balances
        start_time = time.perf_counter_ns()
        tx_receipt = accnt.l1.release_funds(msg, [] if proof is None else [proof], root, gas_attempts=self.GAS_ATTEMPTS)
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
        self.log.info('  l2_cost:               %s', l1_cost)
        self.log.info('  l1_delta (inc):        %s', l1_after-l1_before)
        self.log.info('  l1_delta (with cost):  %s', l1_after-l1_before+l1_cost)
        self.log.info('  l2_delta (dec):        %s', l2_before-l2_after)
        self.log.info('  l2_delta (with cost):  %s', l2_before-l2_after-l2_cost)
        self.assertTrue(l1_after-l1_before+l1_cost == transfer,
                        assertMessage='L1 balance should increase by transfer amount plus gas for releasing')
