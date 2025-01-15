import time, rlp
from web3._utils.events import EventLogErrorFlags
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties
from ten.test.helpers.merkle_tree import MerkleTreeHelper


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 2000000000000000

        # create the bridge user
        accnt = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')
        l1_before = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)

        # send two transactions in quick succession, store details for the second one
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

        logs = accnt.l2.bus.contract.events.ValueTransfer().process_receipt(tx_receipt, EventLogErrorFlags.Ignore)
        value_transfer = accnt.l2.get_value_transfer_event(logs[0])

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

        # release the funds from one transfer
        tx_receipt = accnt.l1.release_funds(msg, proof, root)
        l1_cost = int(tx_receipt.gasUsed) * int(tx_receipt.effectiveGasPrice)
        l1_after = accnt.l1.web3.eth.get_balance(accnt.l1.account.address)
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
