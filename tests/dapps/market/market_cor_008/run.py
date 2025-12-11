from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.dapps.market.seller import MarketDappSeller
from ten.test.dapps.market.buyer import MarketDappBuyer
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        seller1 = MarketDappSeller(self, id=1)
        seller2 = MarketDappSeller(self, id=2)
        buyer1 = MarketDappBuyer(self, id=1)
        buyer2 = MarketDappBuyer(self, id=2)
        players = [seller1, seller2, buyer1, buyer2]

        # the initial balances
        for p in players: p.store_balances('start')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 550)
        _, round_id = admin.create_default_round(duration=60)

        # buyers and sellers place their deposits and stakes
        seller1.approve_and_deposit(round_id, seller1.web3.to_wei(700, 'ether'))
        seller2.approve_and_deposit(round_id, seller2.web3.to_wei(500, 'ether'))
        buyer1.approve_and_stake(round_id, buyer1.web3.to_wei(350, 'ether'))
        buyer2.approve_and_stake(round_id, buyer2.web3.to_wei(900, 'ether'))

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)
        for b in [buyer1, buyer2]: b.redeem_and_forfeit(round_id)
        for s in [seller1, seller2]: s.claim_and_withdraw(round_id)

        # the final balances
        for p in players: p.store_balances('end')
        for p in players: p.log_stored_balances(delta=('end', 'start'))

        # check the seller amounts
        round = admin.get_round(round_id)
        pool_size = round.totalBuyerTEN if round.totalBuyerTEN < round.tenCap else round.tenCap
        self.log.info('Pool size = %d' % pool_size)

        sellers_total_delta = 0
        for s in [seller1, seller2]:
            seller_delta = s.balances['start'].ten - s.balances['end'].ten
            self.log.info('%s %d ten deltas:' % (type(s).__name__, s.id))
            self.log.info('  actual = %.3f' % s.web3.from_wei(seller_delta, 'ether'))
            self.log.info('  actual = %d WEI' % seller_delta)
            sellers_total_delta += seller_delta
        self.log.info('Sellers total ten delta = %d' % sellers_total_delta)
        self.assertTrue((sellers_total_delta - pool_size) < 10, assertMessage='Sellers total delta ten should be the pool size within tolerance')

        buyers_total_delta = 0
        for b in [buyer1, buyer2]:
            buyer_delta = b.balances['end'].ten - b.balances['start'].ten
            self.log.info('%s %d ten deltas:' % (type(b).__name__, b.id))
            self.log.info('  actual = %.3f' % b.web3.from_wei(buyer_delta, 'ether'))
            self.log.info('  actual = %d WEI' % buyer_delta)
            buyers_total_delta += buyer_delta
        self.log.info('Buyers bought actual = %d' % buyers_total_delta)
        self.assertTrue((pool_size - buyers_total_delta) < 10, assertMessage='Buyers total delta ten should be the pool size within tolerance')

