from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.utils.bridge import BridgeUser


class PySysTest(TenNetworkTest):
    PK = None
    AMOUNT = 1

    def execute(self):
        props = Properties()
        pk = self.PK if self.PK is not None else props.l1_funded_account_pk(self.env)
        accnt1 = BridgeUser(self, pk, pk, 'accnt1', check_funds=False)
        amount = accnt1.l1.web3.to_wei(self.AMOUNT, 'ether')

        l1_balance_before = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance_before = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)

        self.log.info('Send native and wait for the xchain message on the L2')
        tx_receipt, xchain_msg = accnt1.l1.send_native(accnt1.l2.account.address, amount, timeout=120)
        accnt1.l2.wait_for_message(xchain_msg)

        l1_balance_after = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance_after = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)

        self.log.info('Account balances;')
        self.log.info('   L1 before: %d', l1_balance_before)
        self.log.info('   L1 after:  %d', l1_balance_after)
        self.log.info('   L1 decr:   %d', (l1_balance_before-l1_balance_after))
        self.log.info('   L2 before: %d', l2_balance_before)
        self.log.info('   L2 after:  %d', l2_balance_after)
        self.log.info('   L2 incr:   %d', (l2_balance_after-l2_balance_before))

        self.assertTrue(l1_balance_before-l1_balance_after > amount)
        self.assertTrue(l2_balance_after-l2_balance_before == amount)
