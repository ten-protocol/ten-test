from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.dapps.market.seller import MarketDappSeller
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        seller = MarketDappSeller(self, id=1)

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 550)
        _, round_id = admin.create_default_round(duration=60)

        # deposit the sellers ten tokens, getting the balances before and after
        nft_balance_before = seller.nft_balance(round_id)
        ten_balance_before, usdc_balance_before = seller.token_balances()
        seller.approve_and_deposit(round_id, seller.web3.to_wei(500, 'ether'))
        nft_balance_after = seller.nft_balance(round_id)
        ten_balance_after, usdc_balance_after = seller.token_balances()

        # check the sellers balances are reduced as expected
        self.assertTrue(nft_balance_after - nft_balance_before == seller.nft_balance(round_id), assertMessage='NFT balance should increase as expected')
        self.assertTrue(ten_balance_before - ten_balance_after == seller.nft_balance(round_id), assertMessage='TEN should decrease as expected')
        self.assertTrue(usdc_balance_before-usdc_balance_after == 0, assertMessage='USDC should stay the same')

        # cancel the round, freeze the sellers and try to withdraw the unused ten back
        admin.increase_evm_time(duration=60)
        admin.cancel_if_under_min(round_id)
        admin.get_round(round_id).to_log(self)

        usdc_claimable = seller.claimable_usdc(round_id)
        ten_claimable = seller.claimable_ten(round_id)
        self.assertTrue(usdc_claimable == 0, assertMessage='Zero usdc claimable as there were no buyers')
        self.assertTrue(ten_claimable == seller.nft_balance(round_id), assertMessage='Full amount of ten should be claimable')

        seller.withdraw_unused_ten(round_id, ten_claimable)
        ten_balance_end, usdc_balance_end = seller.token_balances()
        self.assertTrue(ten_balance_before == ten_balance_end, assertMessage='TEN balance should return to original')
        self.assertTrue(usdc_balance_before == usdc_balance_end, assertMessage='USDC balance should return to original')