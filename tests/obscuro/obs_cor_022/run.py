from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.bridge import BridgeUser
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):
    NAME = 'HubbaBubbaBandit'
    SYMB = 'HBB'

    def execute(self):
        props = Properties()
        transfer = 10000

        funded = BridgeUser(self, props.l1_funded_account_pk(self.env), props.account2pk(), 'funded')
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')
        balance_before = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)

        self.log.info('Send native and wait for the xchain msg on the L2')
        tx_receipt, xchain_msg = funded.l1.send_native(accnt1.l2.account.address, transfer)
        accnt1.l2.wait_for_message(xchain_msg)
        balance_after = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)

        self.assertTrue(balance_after-balance_before == transfer)