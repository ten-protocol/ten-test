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
        buyer2 = MarketDappBuyer(self, pk=Properties().account3pk(), id=2)
        buyer3 = MarketDappBuyer(self, pk=Properties().account4pk(), id=2)
        players = [seller1, buyer1, buyer2, buyer3]

        # the initial balances
        for p in players: p.store_balances('start')

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 500)
        _, round_id = admin.create_default_round(duration=60)

        # buyers and sellers place their deposits and stakes
        seller1.approve_and_deposit(round_id, seller1.web3.to_wei(1000, 'ether'))
        buyer1.approve_and_stake(round_id, buyer1.web3.to_wei(200, 'ether'))
        buyer2.approve_and_stake(round_id, buyer2.web3.to_wei(300, 'ether'))
        buyer3.approve_and_stake(round_id, buyer2.web3.to_wei(500, 'ether'))

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round_id)

        buyer1.redeem_and_forfeit(round_id)
        seller1.claim_and_withdraw(round_id)
        for p in players: p.store_balances('b1_redeem')

        buyer2.redeem_and_forfeit(round_id)
        seller1.claim_and_withdraw(round_id)
        for p in players: p.store_balances('b2_redeem')

        buyer3.redeem_and_forfeit(round_id)
        seller1.claim_and_withdraw(round_id)
        for p in players: p.store_balances('b3_redeem')

        # the final balances
        for p in players: p.store_balances('end')
        for p in players: p.log_stored_balances(delta=('end', 'start'))
