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
        buyer3 = MarketDappBuyer(self, id=2)
        players = [seller1, buyer1, buyer2, buyer3]

        # the initial balances
        for p in players: p.store_balances('start')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 550)
        _, round_id = admin.create_default_round(duration=60)

        # buyers and sellers place their deposits and stakes
        seller1.approve_and_deposit(round_id, seller1.web3.to_wei(1000, 'ether'))
        b1_position = buyer1.approve_and_stake(round_id, buyer1.web3.to_wei(200, 'ether'))
        b2_position = buyer2.approve_and_stake(round_id, buyer2.web3.to_wei(300, 'ether'))
        b3_position = buyer3.approve_and_stake(round_id, buyer2.web3.to_wei(500, 'ether'))

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)

        # buyer 1 redeems their 200 ten, so seller1 usdc should claim 200*1.1
        buyer1.redeem_and_forfeit(round_id)
        seller1.claim_and_withdraw(round_id)
        for p in players: p.store_balances('b1_redeem')

        # buyer 2 redeems their 300 ten, so seller1 usdc should claim 300*1.1
        buyer2.redeem_and_forfeit(round_id)
        seller1.claim_and_withdraw(round_id)
        for p in players: p.store_balances('b2_redeem')

        # buyer 3 redeems their 500 ten, so seller1 usdc should claim 500*1.1
        buyer3.redeem_and_forfeit(round_id)
        seller1.claim_and_withdraw(round_id)
        for p in players: p.store_balances('b3_redeem')

        # the final balances
        for p in players: p.store_balances('end')
        for p in players: p.log_stored_balances(delta=('end', 'start'))

        # check each claim goes up by the expected amount
        self.assertTrue(
            seller1.balances['b1_redeem'].usdc - seller1.balances['start'].usdc == 0.98*buyer1.positions[b1_position].cost_usdc,
            assertMessage='Seller usdc should go up by the buyer1 usdc stake'
        )
        self.assertTrue(
            seller1.balances['b2_redeem'].usdc - seller1.balances['b1_redeem'].usdc == 0.98*buyer2.positions[b2_position].cost_usdc,
            assertMessage='Seller usdc should go up by the buyer2 usdc stake'
        )
        self.assertTrue(
            seller1.balances['b3_redeem'].usdc - seller1.balances['b2_redeem'].usdc == 0.98*buyer3.positions[b3_position].cost_usdc,
            assertMessage='Seller usdc should go up by the buyer3 usdc stake'
        )