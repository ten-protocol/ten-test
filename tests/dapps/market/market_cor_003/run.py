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

        # approve and then buy the protected tokens
        ten_balance_before, usdc_balance_before = buyer.get_token_balances()
        cost_stake, cost_usdc = buyer.approve_stakes(round_id, buy_amount)
        _, position_id = buyer.buy_protected_tokens(round_id, buy_amount)
        ten_balance_after, usdc_balance_after = buyer.get_token_balances()

        # check the buyers balances are reduced as expected
        self.assertTrue(ten_balance_before-ten_balance_after == cost_stake, assertMessage='TEN should decrease as expected')
        self.assertTrue(usdc_balance_before-usdc_balance_after == cost_usdc, assertMessage='USDC should decrease as expected')

        # close the round with it never trading out and forfeit the tokens
        admin.increase_evm_time(duration=60)
        buyer.forfeit_protected_tokens(round_id, position_id, buy_amount)
        ten_balance_forfeit, usdc_balance_forfeit = buyer.get_token_balances()

        # check the buyers balances are return to the original amounts
        self.assertTrue(ten_balance_before == ten_balance_forfeit, assertMessage='TEN should be back to original')
        self.assertTrue(usdc_balance_before == usdc_balance_forfeit, assertMessage='USDC should be back to original')

