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
        seller1 = MarketDappSeller(self, pk=Properties().account2pk(), id=1, amount=700)
        seller2 = MarketDappSeller(self, pk=Properties().account3pk(), id=2, amount=500)
        buyer1 = MarketDappBuyer(self, pk=Properties().account1pk(), id=1, amount=500)
        players = [seller1, seller2, buyer1]

        # the initial balances
        for p in players: p.store_balances('start')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 500)
        _, round_id = admin.create_default_round(duration=60)

        # buyers and sellers both commit the min for the round to go ahead
        for s in [seller1, seller2]:
            s.approve_deposit(s.sell_amount)
            s.deposit_ten_tokens(round_id, s.sell_amount)
        _, cost_usdc = buyer1.approve_stakes(round_id, buyer1.buy_amount)
        _, position_id = buyer1.buy_protected_tokens(round_id, buyer1.buy_amount)

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)
        buy_redeemable = buyer1.get_redeemable_ten(position_id)
        buyer1.redeem_protected_tokens(round_id, position_id, buy_redeemable)
        for s in [seller1, seller2]:
            s.claim_seller_usdc(round_id)
            claimable_ten = s.claimable_seller_ten(round_id)
            self.log.info('Claimable ten back for seller %s is %.3f' % (s.id, s.web3.from_wei(abs(claimable_ten), 'ether')))
            s.withdraw_unused_ten(round_id, claimable_ten)

        # the final balances
        for p in players: p.store_balances('end')
        for p in players: p.log_stored_balances(delta=('end', 'start'))

        seller1_end_usdc = (seller1.sell_amount/120)*cost_usdc
        seller2_end_usdc = (seller2.sell_amount/120)*cost_usdc