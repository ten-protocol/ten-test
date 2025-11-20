from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.dapps.market.seller import MarketDappSeller
from ten.test.dapps.market.buyer import MarketDappBuyer
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        seller = MarketDappSeller(self, pk=Properties().account2pk(), id=1)
        buyer = MarketDappBuyer(self, pk=Properties().account1pk(), id=1)
        players = [seller, buyer]

        # the initial balances
        for p in players: p.store_balances('start')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 500)
        _, round_id = admin.create_default_round(duration=60)

        # buyers and sellers both commit the min for the round to go ahead
        seller.approve_and_deposit(round_id, seller.web3.to_wei(500, 'ether'))
        buyer.approve_and_stake(round_id, buyer.web3.to_wei(500, 'ether'))

        # round deadline exceeds, sellers are frozen, buyers redeem tokens, sellers claim their usdc
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)
        buyer.redeem_and_forfeit(round_id)
        seller.claim_and_withdraw(round_id)

        # the final balances
        for p in players: p.store_balances('end')
        for p in players: p.log_stored_balances(delta=('end', 'start'))

        # check the ten and usdc balance change as expected
        total_amount, total_cost_stake, total_cost_usdc = buyer.get_total_staked(round_id)
        self.assertTrue(seller.balances['end'].ten == seller.balances['start'].ten - total_amount, assertMessage='Seller ten decreases')
        self.assertTrue(seller.balances['end'].usdc == seller.balances['start'].usdc + total_cost_usdc, assertMessage='Seller usdc increases')
        self.assertTrue(buyer.balances['end'].ten == buyer.balances['start'].ten + total_amount, assertMessage='Buyer ten increases')
        self.assertTrue(buyer.balances['end'].usdc == buyer.balances['start'].usdc - total_cost_usdc, assertMessage='Buyer ten decreases')

