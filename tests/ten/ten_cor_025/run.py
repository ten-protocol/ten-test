import time
from web3._utils.events import EventLogErrorFlags
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties
from ten.test.helpers.merkle_tree import MerkleTreeHelper


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 2000000000000000
        proof_timeout = 90 if self.is_local_ten() else 2400

        # create the bridge user
        accnt = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')
        l1_before = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)

        # send four transactions in quick succession, store details for the second one
        params = {'from': accnt.l2.account.address,
                  'chainId': accnt.l2.web3.eth.chain_id,
                  'gasPrice': accnt.l2.web3.eth.gas_price,
                  'value':transfer}
        gas_limit = accnt.l2.bridge.contract.functions.sendNative(accnt.l1.account.address).estimate_gas(params)
        nonce1, tx_sign1 = self.create_signed(accnt, transfer, gas_limit)
        nonce2, tx_sign2 = self.create_signed(accnt, transfer, gas_limit)
        nonce3, tx_sign3 = self.create_signed(accnt, transfer, gas_limit)
        nonce4, tx_sign4 = self.create_signed(accnt, transfer, gas_limit)
        self.send_tx(accnt, nonce1, tx_sign1)
        self.send_tx(accnt, nonce2, tx_sign2)
        self.send_tx(accnt, nonce3, tx_sign3)
        tx_hash = self.send_tx(accnt, nonce4, tx_sign4)
        tx_receipt = self.wait_tx(accnt, nonce4, tx_hash)

        logs = accnt.l2.bus.contract.events.LogMessagePublished().process_receipt(tx_receipt, EventLogErrorFlags.Discard)
        log_msg = accnt.l2.get_cross_chain_message(logs[0])

        # get the log msg from the merkle tree helper
        mh = MerkleTreeHelper.create(self)
        block, decoded = mh.dump_tree(accnt.l2.web3, tx_receipt, 'xchain_tree.log')
        msg, msg_hash = mh.process_log_msg(log_msg)
        self.log.info('  value_transfer:        %s', msg)
        self.log.info('  value_transfer_hash:   %s', msg_hash)
        self.log.info('  decoded_cross_chain:   %s', decoded)
        self.log.info('  merkle_root:           %s', block.crossChainTreeHash)
        self.assertTrue(msg_hash in [x[1] for x in decoded], assertMessage='Value transfer should be in the xchain tree')

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

            # release the funds from one transfer
            tx_receipt = accnt.l1.release_funds(msg, proof, root)
            l1_cost = int(tx_receipt.gasUsed) * int(tx_receipt.effectiveGasPrice)
            l1_after = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)

            # wait for the L1 balance to go up
            start = time.time()
            while (l1_after <= l1_before):
                l1_after = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)
                if time.time() - start > 30: raise TimeoutError('Timed out waiting for L1 balance to increase')
                self.log.info('Waiting for L1 balance to increase')
                time.sleep(1.0)

            self.log.info('  l1_balance before:     %s', l1_before)
            self.log.info('  l1_balance after:      %s', l1_after)
            self.log.info('  l1_cost:               %s', l1_cost)
            self.log.info('  l1_delta (inc):        %s', l1_after-l1_before)
            self.log.info('  l1_delta (with cost):  %s', l1_after-l1_before+l1_cost)
            self.assertTrue(l1_after-l1_before+l1_cost == transfer,
                            assertMessage='L1 balance should increase by transfer amount plus gas for releasing')

    def create_signed(self, user, amount, gas_limit):
        nonce = user.l2.network.get_next_nonce(self, user.l2.web3, user.l2.account.address, True, False)
        tx = user.l2.bridge.contract.functions.sendNative(user.l1.account.address).build_transaction(
            {
                'nonce': nonce,
                'chainId': user.l2.web3.eth.chain_id,
                'gas': gas_limit,
                'gasPrice': user.l2.web3.eth.gas_price,
                'value': amount + int(user.l2.send_native_fees())
            }
        )
        tx_sign = user.l2.network.sign_transaction(self, tx, nonce, user.l2.account, True)
        return nonce, tx_sign

    def send_tx(self, user, nonce, tx_sign):
        return user.l2.network.send_transaction(self, user.l2.web3, nonce, user.l2.account.address, tx_sign, True, False)

    def wait_tx(self, user, nonce, tx_hash, timeout=30):
        return user.l2.network.wait_for_transaction(self, user.l2.web3, nonce, user.l2.account.address, tx_hash, True, False, timeout)
