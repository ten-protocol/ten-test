from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.dapps.market.seller import MarketDappSeller
from ten.test.dapps.market.buyer import MarketDappBuyer
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        seller1 = MarketDappSeller(self, pk=Properties().account1pk(), id=1, tokens=2500)
        buyer1 = MarketDappBuyer(self, pk=Properties().account2pk(), id=1, tokens=2500)

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 550)
        _, round1 = admin.create_default_round(duration=60)

        for p in [seller1, buyer1]: p.store_balances('first_start')
        seller1.approve_and_deposit(round1, seller1.web3.to_wei(900, 'ether'))
        buyer1.approve_and_stake(round1, buyer1.web3.to_wei(500, 'ether'))
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round1)
        buyer1.redeem_and_forfeit(round1)
        for p in [seller1, buyer1]: p.store_balances('first_end')
        for p in [seller1, buyer1]: p.log_stored_balances(delta=('first_end', 'first_start'))

        # create another round (price 1.3 USD, co-stake 25%, capped at 1000 with min of 550)
        deadline = int(admin.web3.eth.get_block("latest").timestamp) + 60
        price = admin.web3.to_wei(1.3, 'ether')
        beta = admin.to_ray(0.25)
        ten_cap = admin.web3.to_wei(1000, 'ether')
        min_usdc = admin.web3.to_wei(550, 'ether')
        _, round2 = admin.create_round(deadline, price, beta, ten_cap, 0, min_usdc)

        for p in [seller1, buyer1]: p.store_balances('second_start')
        seller1.approve_and_deposit(round2, seller1.web3.to_wei(1000, 'ether'))
        buyer1.approve_and_stake(round2, buyer1.web3.to_wei(800, 'ether'))
        admin.increase_evm_time(duration=60)
        admin.freeze_sellers(round2)
        buyer1.redeem_and_forfeit(round2)
        seller1.claim_and_withdraw(round2)
        seller1.claim_and_withdraw(round1)
        for p in [seller1, buyer1]: p.store_balances('second_end')
        for p in [seller1, buyer1]: p.log_stored_balances(delta=('second_end', 'first_start'))

        self.assertTrue(seller1.balances['first_end'].usdc - seller1.balances['first_start'].usdc == 0,
                        assertMessage='Seller USDC should not change')
        self.assertTrue(seller1.balances['second_end'].usdc - seller1.balances['first_start'].usdc == seller1.web3.to_wei(1590, 'ether'),
                        assertMessage='Seller USDC should change when both collected')
        self.assertTrue(seller1.balances['first_start'].ten - seller1.balances['first_end'].ten == seller1.web3.to_wei(900, 'ether'),
                        assertMessage='Seller TEN should go down by deposit')
        self.assertTrue(seller1.balances['first_start'].ten - seller1.balances['second_end'].ten == seller1.web3.to_wei(1300, 'ether'),
                        assertMessage='Seller TEN should go down by amount bought')

        self.assertTrue(buyer1.balances['first_start'].usdc - buyer1.balances['second_end'].usdc == buyer1.web3.to_wei(1590, 'ether'),
                        assertMessage='Buyer USDC should change in total as expected')
        self.assertTrue(buyer1.balances['second_end'].ten - buyer1.balances['first_start'].ten == buyer1.web3.to_wei(1300, 'ether'),
                        assertMessage='Buyer TEN should change in total as expected')

