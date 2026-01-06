from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()

        # create the users for the test
        funded = BridgeUser(self, props.l1_funded_account_pk(self.env), props.account2pk(), 'funded')
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        # the symbol and amount we are going to bridge
        sym = 'WETH'
        amount = 5

        # deposit some ETH into the contract
        self.log.info('')
        self.log.info('Deposit wrapped ETH')
        funded.l1.deposit_weth(100)
        accnt1.l1.deposit_weth(100)

        # account1 approves the bridge to transfer
        self.log.info('')
        self.log.info('Approve tokens')
        accnt1.l1.approve_token(sym, accnt1.l1.bridge.address, 100)

        # send some tokens across the bridge
        self.log.info('')
        self.log.info('Send tokens on the L1 to cross the bridge')
        _, xchain_msg = accnt1.l1.send_erc20(sym, accnt1.l2.account.address, amount)
        accnt1.l2.wait_for_message(xchain_msg)

        self.log.info('Relay the send tokens request')
        _ = accnt1.l2.relay_message(xchain_msg)

        # print out the balances and perform test validation
        self.log.info('Print out token balances')
        balance_l1 = accnt1.l1.balance_for_token(sym)
        balance_l2 = accnt1.l2.balance_for_token(sym)
        self.log.info('    Account1 ERC20 balance L1 = %d ', balance_l1)
        self.log.info('    Account1 ERC20 balance L2 = %d ', balance_l2)
        self.assertTrue(balance_l1 == 200 - amount)
        self.assertTrue(balance_l2 == amount)
