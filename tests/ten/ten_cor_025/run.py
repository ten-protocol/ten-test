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

        # send two transactions in quick succession, store details for the second one
        params = {'from': accnt.l2.account.address,
                  'chainId': accnt.l2.web3.eth.chain_id,
                  'gasPrice': accnt.l2.web3.eth.gas_price,
                  'value':transfer}
        gas_limit = accnt.l2.bridge.contract.functions.sendNative(accnt.l1.account.address).estimate_gas(params)
        nonce1, tx_sign1 = self.create_signed(accnt, transfer, gas_limit)
        nonce2, tx_sign2 = self.create_signed(accnt, transfer, gas_limit)
        self.send_tx(accnt, nonce1, tx_sign1)
        tx_hash = self.send_tx(accnt, nonce2, tx_sign2)
        tx_receipt = self.wait_tx(accnt, nonce2, tx_hash)
        value_transfer = accnt.l2.bus.contract.events.ValueTransfer().process_receipt(tx_receipt, EventLogErrorFlags.Ignore)

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

    def create_signed(self, user, amount, gas_limit):
        nonce = user.l2.network.get_next_nonce(self, user.l2.web3, user.l2.account, True, False)
        tx = user.l2.bridge.contract.functions.sendNative(user.l1.account.address).build_transaction(
            {
                'nonce': nonce,
                'chainId': user.l2.web3.eth.chain_id,
                'gas': gas_limit,
                'gasPrice': user.l2.web3.eth.gas_price,
                'value': amount
            }
        )
        tx_sign = user.l2.network.sign_transaction(self, tx, nonce, user.l2.account, True)
        return nonce, tx_sign

    def send_tx(self, user, nonce, tx_sign):
        return user.l2.network.send_transaction(self, user.l2.web3, nonce, user.l2.account, tx_sign, True, False)

    def wait_tx(self, user, nonce, tx_hash, timeout=30):
        return user.l2.network.wait_for_transaction(self, user.l2.web3, nonce, user.l2.account, tx_hash, True, False, timeout)
