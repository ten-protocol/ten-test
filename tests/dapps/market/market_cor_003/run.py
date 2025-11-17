from web3 import Web3
from ten.test.utils.properties import Properties
from ten.test.basetest import TenNetworkTest
from ten.test.dapps.market.buyer import MarketDappBuyer
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        buyer = MarketDappBuyer(self, pk=Properties().account1_1pk())
        buy_amount = Web3().to_wei(100, 'ether')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 500)
        _, round_id = admin.create_default_round(duration=60)
        self.log.info('Round created with id = %d' % round_id)

        # log out the initial token balances
        ten_balance_before = buyer.ten_balance()
        usdc_balance_before = buyer.usdc_balance()
        self.log.info('  TEN balance before = %d ', ten_balance_before)
        self.log.info('  USDC balance before = %d ', usdc_balance_before)

        # buyer 1 is going to go for 100 tokens
        cost_stake, cost_usdc = buyer.approve_stakes(round_id, buy_amount)

        # account 1 buys into the market
        _, position_id = buyer.buy_protected_tokens(round_id, buy_amount)
        ten_balance_after = buyer.ten_balance()
        usdc_balance_after = buyer.usdc_balance()
        self.log.info('  TEN balance after  = %d ', ten_balance_after)
        self.log.info('  USDC balance after  = %d ', usdc_balance_after)

        # check the buyers balances are reduced as expected
        self.assertTrue(ten_balance_before-ten_balance_after == cost_stake, assertMessage='TEN should decrease as expected')
        self.assertTrue(usdc_balance_before-usdc_balance_after == cost_usdc, assertMessage='USDC should decrease as expected')

        # close the round with it never trading out
        admin.increase_evm_time(duration=60)
        is_active = admin.market.contract.functions.isActive(round_id).call()
        self.log.info('Latest round %d is_active = %s' % (round_id, is_active))

        # forfeit the tokens
        buyer.forfeit_protected_tokens(round_id, position_id, buy_amount)
        ten_balance_forfeit = buyer.ten_balance()
        usdc_balance_forfeit = buyer.usdc_balance()
        self.log.info('  TEN balance on forfeit  = %d ', ten_balance_forfeit)
        self.log.info('  USDC balance on forfeit  = %d ', usdc_balance_forfeit)

        # check the buyers balances are return to the original amounts
        self.assertTrue(ten_balance_before == ten_balance_forfeit, assertMessage='TEN should be back to original')
        self.assertTrue(usdc_balance_before == usdc_balance_forfeit, assertMessage='USDC should be back to original')

