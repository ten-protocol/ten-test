from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.dapps.market.seller import MarketDappSeller
from ten.test.dapps.market.buyer import MarketDappBuyer
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        seller1 = MarketDappSeller(self, pk=Properties().account2pk(), id=1)
        seller2 = MarketDappSeller(self, pk=Properties().account3pk(), id=2)
        buyer1 = MarketDappBuyer(self, pk=Properties().account1pk(), id=1)
        players = [seller1, seller2, buyer1]

        # the initial balances
        for p in players: p.store_balances('start')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 550)
        _, round_id = admin.create_default_round(duration=60)

        # buyers and sellers both commit the min for the round to go ahead
        seller1.approve_and_deposit(round_id, seller1.web3.to_wei(700, 'ether'))
        seller2.approve_and_deposit(round_id, seller2.web3.to_wei(500, 'ether'))
        buyer1.approve_and_stake(round_id, buyer1.web3.to_wei(500, 'ether'))

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)
        buyer1.redeem_and_forfeit(round_id)
        for s in [seller1, seller2]: s.claim_and_withdraw(round_id)

        # the final balances
        for p in players: p.store_balances('end')
        for p in players: p.log_stored_balances(delta=('end', 'start'))

        # check the seller amounts
        round = admin.get_round(round_id)
        distribute = round.totalBuyerTEN if round.totalBuyerTEN < round.tenCap else round.tenCap
        ratio = (distribute / round.tenCap)
        sum_ten_expect = 0
        sum_ten_actual = 0
        for s in [seller1, seller2]:
            ten_expected = ratio * (s.nft_balance(round_id) * round.sellerScale) / 1e18
            ten_actual = s.balances['start'].ten-s.balances['end'].ten
            self.log.info('%s %d ten deltas:' % (type(s).__name__, s.id))
            self.log.info('  expected = %.3f' % seller1.web3.from_wei(ten_expected, 'ether'))
            self.log.info('  actual = %.3f' % seller1.web3.from_wei(ten_actual, 'ether'))
            self.log.info('  actual = %d WEI' % ten_actual)
            sum_ten_expect += ten_expected
            sum_ten_actual += ten_actual
        self.log.info('Sold actual = %d' % sum_ten_actual)
        self.log.info('Bought actual = %d' % distribute)
        self.assertTrue(sum_ten_expect == distribute, assertMessage='Expected should be the total bought')

        # rounding means sellers may give a few more of their TEN over in total
        self.assertTrue((sum_ten_actual - distribute) < 10, assertMessage='Actual should be the total bought within tolerance')



