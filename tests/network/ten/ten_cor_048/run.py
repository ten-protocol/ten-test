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
        amount = 10_000

        # check the weth balance and deposit some more if required
        self.log.info('')
        self.log.info('Deposit wrapped ETH (units are in wei)')
        balance = accnt1.l1.balance_for_token(sym)
        self.log.info('Account1 ERC20 balance before = %d ', balance)
        if balance < 1_000_000:
            accnt1.l1.deposit_weth(1_000_000)
            self.log.info('Account1 ERC20 balance after  = %d ', accnt1.l1.balance_for_token(sym))
        else:
            self.log.info('Sufficient balance exists in weth on this account')

        # check how much the bridge is approved to spend for the account and approve
        # more if required
        self.log.info('')
        self.log.info('Approve token')
        allowance = accnt1.l1.allowance_for_token(sym, accnt1.l1.bridge.address)
        self.log.info('Account1 ERC20 bridge allowance before = %d ', allowance)
        if allowance < 100_000:
            accnt1.l1.approve_token(sym, accnt1.l1.bridge.address, 100_000)
            self.log.info('Account1 ERC20 bridge allowance after  = %d ', accnt1.l1.allowance_for_token(sym, accnt1.l1.bridge.address))
        else:
            self.log.info('Sufficient allowance exists in weth on this account')

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
