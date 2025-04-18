from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties
from ten.test.helpers.merkle_tree import MerkleTreeHelper
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber

class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 4000000000000000
        proof_timeout = 90

        # create the bridge user and subscribe for value transfer events
        accnt = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')
        l1_before = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)
        l2_before = accnt.l2.web3.eth.get_balance(accnt.l2.account.address)

        subscriber = AllEventsLogSubscriber(self, accnt.l2.network, accnt.l2.bus.address, accnt.l2.bus.abi_path)
        subscriber.run()

        # send funds from the L2 to the L1
        self.log.info('Send native from L2 to L1')
        self.log.info('Fees to send are %d' % accnt.l2.send_native_fees())
        tx_receipt, log_message = accnt.l2.send_native(accnt.l1.account.address, transfer, dump_file='send_native.tx')
        l2_cost = int(tx_receipt.gasUsed) * accnt.l2.web3.eth.gas_price

        # get the log msg from the merkle tree helper
        mh = MerkleTreeHelper.create(self)
        block, decoded = mh.dump_tree(accnt.l2.web3, tx_receipt, 'xchain_tree.log')
        msg, msg_hash = mh.process_log_msg(log_message)
        self.log.info('  value_transfer:        %s', msg)
        self.log.info('  value_transfer_hash:   %s', msg_hash)
        self.log.info('  decoded_cross_chain:   %s', decoded)
        self.log.info('  block_merkle_root:     %s', block.crossChainTreeHash)
        self.assertTrue(msg_hash in [x[1] for x in decoded], assertMessage='Log message should be in the xchain tree')

        mh_root, mh_proof = mh.get_proof('xchain_tree.log', 'm,%s' % msg_hash)
        self.log.info('  calculated root:       %s', mh_root)
        self.assertTrue(block.crossChainTreeHash == mh_root, assertMessage='Calculated merkle root should be same as the block header')

        # if a local testnet wait for the xchain message on the L1 and release the funds
        if self.is_local_ten():
            # get the root and proof of inclusion from the node
            self.log.info('Request proof and root from the node')
            root, proof = accnt.l2.wait_for_proof('m', msg_hash, proof_timeout)
            self.log.info('  returned root:         %s', root)
            self.log.info('  returned proof:        %s', [p.hex() for p in proof])

            # release the funds from the L1 and check the balances
            self.log.info('Relay the message on the L1 to release them')
            tx_receipt = accnt.l1.release_funds(msg, proof, root)

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
