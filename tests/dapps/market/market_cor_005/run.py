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
        self.log.info('  NFT blance before  = %d ', nft_balance_before)
        self.log.info('  NFT blance after = %d ', nft_balance_after)

        # check the sellers balances are reduced as expected
        self.assertTrue(ten_balance_before-ten_balance_after == sell_amount, assertMessage='TEN should decrease as expected')
        self.assertTrue(usdc_balance_before-usdc_balance_after == 0, assertMessage='USDC should stay the same')
        self.assertTrue(nft_balance_after-nft_balance_before == sell_amount, assertMessage='NFT balance should increase as expected')

        # close the round
        admin.increase_evm_time(duration=60)
