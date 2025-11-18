from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.dapps.market.seller import MarketDappSeller
from ten.test.dapps.market.buyer import MarketDappBuyer
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        seller = MarketDappSeller(self, pk=Properties().account2pk())
        sell_amount = Web3().to_wei(500, 'ether')
        buyer = MarketDappBuyer(self, pk=Properties().account1pk())
        buy_amount = Web3().to_wei(500, 'ether')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 500)
        _, round_id = admin.create_default_round(duration=60)

        # the initial balances
        seller_ten_start, seller_usdc_start = seller.get_token_balances()
        buyer_ten_start, buyer_usdc_start = buyer.get_token_balances()

        # buyers and sellers both commit the min for the round to go ahead
        seller.approve_deposit(sell_amount)
        seller.deposit_ten_tokens(round_id, sell_amount)
        _, cost_usdc = buyer.approve_stakes(round_id, buy_amount)
        _, position_id = buyer.buy_protected_tokens(round_id, buy_amount)

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)
        buy_redeemable = buyer.get_redeemable_ten(position_id)
        buyer.redeem_protected_tokens(round_id, position_id, buy_redeemable)
        seller.claim_seller_usdc(round_id)

        # the final balances
        seller_ten_end, seller_usd_end = seller.get_token_balances()
        buyer_ten_end, buyer_usd_end = buyer.get_token_balances()

        # check the ten and usdc balance change as expected
        self.assertTrue(seller_ten_end == seller_ten_start - sell_amount)
        self.assertTrue(seller_usd_end == seller_usdc_start + cost_usdc)
        self.assertTrue(buyer_ten_end == buyer_ten_start + buy_amount)
        self.assertTrue(buyer_usd_end == buyer_usdc_start - cost_usdc)

