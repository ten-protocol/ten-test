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
        seller = MarketDappSeller(self, pk=Properties().account2pk(), id=1, amount=500)
        buyer = MarketDappBuyer(self, pk=Properties().account1pk(), id=1, amount=500)
        players = [seller, buyer]

        # the initial balances
        for p in players: p.store_balances('start')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 500)
        _, round_id = admin.create_default_round(duration=60)

        # buyers and sellers both commit the min for the round to go ahead
        seller.approve_deposit(seller.sell_amount)
        seller.deposit_ten_tokens(round_id, seller.sell_amount)
        _, cost_usdc = buyer.approve_stakes(round_id, buyer.buy_amount)
        _, position_id = buyer.buy_protected_tokens(round_id, buyer.buy_amount)

        # round deadline exceeds, sellers are frozen, buyers redeem tokens, sellers claim their usdc
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)
        buy_redeemable = buyer.get_redeemable_ten(position_id)
        buyer.redeem_protected_tokens(round_id, position_id, buy_redeemable)
        seller.claim_seller_usdc(round_id)
        claimable_ten = seller.claimable_seller_ten(round_id)
        self.assertTrue(claimable_ten==0, 'Claimable ten should be zero')

        # the final balances
        for p in players: p.store_balances('end')
        for p in players: p.log_stored_balances(delta=('end', 'start'))

        # check the ten and usdc balance change as expected
        self.assertTrue(seller.balances['end'][0] == seller.balances['start'][0] - seller.sell_amount, assertMessage='Seller ten decreases')
        self.assertTrue(seller.balances['end'][1] == seller.balances['start'][1] + cost_usdc, assertMessage='Seller usdc increases')
        self.assertTrue(buyer.balances['end'][0] == buyer.balances['start'][0] + buyer.buy_amount, assertMessage='Buyer ten increases')
        self.assertTrue(buyer.balances['end'][1] == buyer.balances['start'][1] - cost_usdc, assertMessage='Buyer ten decreases')

