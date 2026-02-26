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
        buyer1 = MarketDappBuyer(self, id=1)
        buyer2 = MarketDappBuyer(self, id=2)
        buyer3 = MarketDappBuyer(self, id=3)
        players = [seller1, buyer1, buyer2, buyer3]

        # the initial balances
        for p in players: p.store_balances('start')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 550)
        _, round_id = admin.create_default_round(duration=60)

        # buyers and sellers place their deposits and stakes
        seller1.approve_and_deposit(round_id, seller1.web3.to_wei(1000, 'ether'))
        b1_position = buyer1.approve_and_stake(round_id, buyer1.web3.to_wei(600, 'ether'))
        b2_position = buyer2.approve_and_stake(round_id, buyer2.web3.to_wei(200, 'ether'))
        b3_position = buyer3.approve_and_stake(round_id, buyer3.web3.to_wei(300, 'ether'))
        for p in players: p.store_balances('middle')

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)

        # buyer2 and 3 forfeit their stake, buyer1 redeems and forfeits remaining (which should be none)
        buyer2.forfeit_stake(round_id, b2_position, buyer2.positions[b2_position].amount)
        buyer3.forfeit_stake(round_id, b3_position, buyer3.positions[b3_position].amount)
        buyer1.redeem_and_forfeit(round_id)
        seller1.claim_and_withdraw(round_id)

        # the final balances
        for p in players: p.store_balances('end')
        for p in players: p.log_stored_balances(delta=('end', 'start'))

        # check each claim goes up by the expected amount
        round = admin.get_round(round_id)
        round.to_log(self)

        WAD = 10**18
        delta = 600 * WAD
        self.assertTrue(
            seller1.balances['start'].ten - seller1.balances['end'].ten == delta,
            assertMessage='Seller ten should be the buyer1 allocation'
        )
        self.assertTrue(
            buyer1.balances['end'].ten - buyer1.balances['start'].ten == delta,
            assertMessage='Buyer1 ten should be the buyer1 amount'
        )
        self.assertTrue(
            buyer2.balances['end'].ten - buyer2.balances['start'].ten == 0,
            assertMessage='Buyer2 ten should be zero'
        )
        self.assertTrue(
            buyer3.balances['end'].ten - buyer3.balances['start'].ten == 0,
            assertMessage='Buyer3 ten should be zero'
        )



