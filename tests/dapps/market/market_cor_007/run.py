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
        for s in [seller1, seller2]: s.approve_and_deposit(round_id, s.sell_amount)
        position_id = buyer1.approve_and_buy(round_id, buyer1.buy_amount)

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

        # check the seller amounts
        round = admin.get_round(round_id)
        ratio = (round.totalBuyerTEN / round.tenCap)
        sum_ten_expect = 0
        sum_ten_actual = 0
        for s in [seller1, seller2]:
            ten_expected = ratio * (s.sell_amount * round.sellerScale) / 1e18
            ten_actual = s.balances['start'][0]-s.balances['end'][0]
            self.log.info('%s %d ten deltas:' % (type(s).__name__, s.id))
            self.log.info('  expected = %.3f' % seller1.web3.from_wei(ten_expected, 'ether'))
            self.log.info('  actual = %.3f' % seller1.web3.from_wei(ten_actual, 'ether'))
            sum_ten_expect += ten_expected
            sum_ten_actual += ten_actual
        self.assertTrue(sum_ten_expect == round.totalBuyerTEN, assertMessage='Excepted should be the total bought')
        self.assertTrue(sum_ten_actual == round.totalBuyerTEN, assertMessage='Actual should be the total bought')
