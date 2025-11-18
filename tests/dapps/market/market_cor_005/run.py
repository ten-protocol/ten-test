from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.dapps.market.seller import MarketDappSeller
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        seller = MarketDappSeller(self, pk=Properties().account2pk())
        sell_amount = Web3().to_wei(500, 'ether')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 500)
        _, round_id = admin.create_default_round(duration=60)

        # deposit the sellers ten tokens, getting the balances before and after
        nft_balance_before = seller.seller_nft_balance(round_id)
        ten_balance_before, usdc_balance_before = seller.get_token_balances()
        seller.approve_deposit(sell_amount)
        seller.deposit_ten_tokens(round_id, sell_amount)
        ten_balance_after, usdc_balance_after = seller.get_token_balances()
        nft_balance_after = seller.seller_nft_balance(round_id)

        # check the sellers balances are reduced as expected
        self.assertTrue(ten_balance_before-ten_balance_after == sell_amount, assertMessage='TEN should decrease as expected')
        self.assertTrue(usdc_balance_before-usdc_balance_after == 0, assertMessage='USDC should stay the same')
        self.assertTrue(nft_balance_after-nft_balance_before == sell_amount, assertMessage='NFT balance should increase as expected')

        # cancel the round, freeze the sellers and try to withdraw the unused ten back
        admin.increase_evm_time(duration=60)
        admin.cancel_if_under_min(round_id)
        admin.freeze_sellers(round_id)
        admin.get_round(round_id).to_log(self)

        usdc_claimable = seller.claimable_seller_usdc(round_id)
        ten_claimable = seller.unused_ten_claimable(round_id)
        self.assertTrue(usdc_claimable == 0, assertMessage='Zero usdc claimable as there were no buyers')
        self.assertTrue(ten_claimable == sell_amount, assertMessage='Full amount of ten should be claimable')