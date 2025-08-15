from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 1000

        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        l1_bridge_before = accnt1.l1.web3.eth.get_balance(props.L1BridgeAddress)
        l1_balance_before = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance_before = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)

        # send native from the L1 to the L2, wait for the xchain msg on the l2
        self.log.info('Send native and wait for the xchain message on the L2')
        tx_receipt, xchain_msg = accnt1.l1.send_native(accnt1.l2.account.address, transfer)
        accnt1.l2.wait_for_message(xchain_msg)

        l1_balance_after = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance_after = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)
        l1_bridge_after = accnt1.l1.web3.eth.get_balance(props.L1BridgeAddress)

        self.log.info('Bridge balances;')
        self.log.info('   Before: %d', l1_bridge_before)
        self.log.info('   After:  %d', l1_bridge_after)
        self.log.info('   Incr:   %d', (l1_bridge_after-l1_bridge_before))
        self.assertTrue(l1_bridge_after-l1_bridge_before == transfer)

        self.log.info('Account balances;')
        self.log.info('   L1 before: %d', l1_balance_before)
        self.log.info('   L1 after:  %d', l1_balance_after)
        self.log.info('   L1 decr:   %d', (l1_balance_before-l1_balance_after))
        self.log.info('   L2 before: %d', l2_balance_before)
        self.log.info('   L2 after:  %d', l2_balance_after)
        self.log.info('   L2 incr:   %d', (l2_balance_after-l2_balance_before))

        self.assertTrue(l1_balance_before-l1_balance_after > transfer)
        self.assertTrue(l2_balance_after-l2_balance_before == transfer)