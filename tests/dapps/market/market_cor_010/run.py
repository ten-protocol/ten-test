from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.dapps.market.seller import MarketDappSeller
from ten.test.dapps.market.buyer import MarketDappBuyer
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        seller1 = MarketDappSeller(self, pk=Properties().account1pk(), id=1)
        buyer1 = MarketDappBuyer(self, pk=Properties().account2pk(), id=1)
        players = [seller1, buyer1]

        # the initial balances
        for p in players: p.store_balances('start')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 550)
        _, round_id = admin.create_default_round(duration=60)

        # buyers and sellers place their deposits and stakes
        seller1.approve_and_deposit(round_id, seller1.web3.to_wei(1000, 'ether'))
        b1_position = buyer1.approve_and_stake(round_id, buyer1.web3.to_wei(1000, 'ether'))

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)

        # buyer 1 redeems 200 ten, so seller1 usdc should claim 200*1.1
        buyer1.redeem_stake(round_id, b1_position, buyer1.web3.to_wei(200, 'ether'))
        seller1.claim_and_withdraw(round_id)
        for p in players: p.store_balances('redeem_1')

        # buyer 1 redeems 300 ten, so seller1 usdc should claim 300*1.1
        buyer1.redeem_stake(round_id, b1_position, buyer1.web3.to_wei(300, 'ether'))
        seller1.claim_and_withdraw(round_id)
        for p in players: p.store_balances('redeem_2')

        # buyer 1 redeems 500 ten, so seller1 usdc should claim 500*1.1
        buyer1.redeem_stake(round_id, b1_position, buyer1.web3.to_wei(500, 'ether'))
        seller1.claim_and_withdraw(round_id)
        for p in players: p.store_balances('redeem_3')

        # the final balances
        for p in players: p.store_balances('end')
        for p in players: p.log_stored_balances(delta=('end', 'start'))

        # check each claim goes up by the expected amount
        self.assertTrue(
            seller1.balances['redeem_1'].usdc - seller1.balances['start'].usdc - 1.1*buyer1.web3.to_wei(200, 'ether') < 10,
            assertMessage='Seller usdc should go up by 200'
        )
        self.assertTrue(
            seller1.balances['redeem_2'].usdc - seller1.balances['redeem_1'].usdc - 1.1*buyer1.web3.to_wei(300, 'ether') < 10,
            assertMessage='Seller usdc should go up by 300'
        )
        self.assertTrue(
            seller1.balances['redeem_3'].usdc - seller1.balances['redeem_2'].usdc - 1.1*buyer1.web3.to_wei(500, 'ether') < 10,
            assertMessage='Seller usdc should go up 500'
        )
        self.assertTrue(
            seller1.balances['redeem_3'].usdc - seller1.balances['start'].usdc == buyer1.positions[b1_position].cost_usdc,
            assertMessage='Seller usdc should go up by the buyer1 usdc stake'
        )
