import random
from ten.test.basetest import TenNetworkTest
from ten.test.dapps.market.admin import MarketDappAdmin
from ten.test.dapps.market.buyer import MarketDappBuyer
from ten.test.dapps.market.seller import MarketDappSeller


class PySysTest(TenNetworkTest):
    MAX_DURATION = 120 # max duration 120 secs

    def execute(self):
        admin = MarketDappAdmin(self)
        admin.increase_evm_time(duration=self.MAX_DURATION)
        self.run_round(admin)

    def run_round(self, admin):
        cap = random.randint(1000,4000)
        min_cap = random.randint(1000,cap)
        duration = random.randint(20, self.MAX_DURATION)
        deadline = int(admin.web3.eth.get_block("latest").timestamp) + duration
        price = admin.web3.to_wei(random.randint(100,190)/100, 'ether')
        beta = admin.web3.to_wei(random.randint(10,100)/100, 'ether') * 10 ** 9
        ten_cap = admin.web3.to_wei(cap, 'ether')
        min_usdc = admin.web3.to_wei(min_cap, 'ether')
        _, round_id = admin.create_round(deadline, price, beta, ten_cap, 0, min_usdc)

        sellers = []
        seller_amount = 0
        while seller_amount < cap:
            amount = random.randint(500,1200)
            seller = MarketDappSeller(self, pk=self.get_ephemeral_pk(), id=len(sellers)+1, tokens=2*amount)
            seller.approve_and_deposit(round_id, seller.web3.to_wei(amount, 'ether'))
            sellers.append(seller)
            seller_amount += amount
        self.log.info('Total sellers deposits is %d for cap %d' % (seller_amount, cap))

        buyers = []
        buyer_amount = 0
        while buyer_amount < min_cap:
            amount = random.randint(500,1200)
            buyer = MarketDappBuyer(self, pk=self.get_ephemeral_pk(), id=len(buyers)+1, tokens=2*amount)
            buyer.approve_and_stake(round_id, buyer.web3.to_wei(amount, 'ether'))
            buyers.append(buyer)
            buyer_amount += amount
        self.log.info('Total buyers stakes is %d for min cap %d' % (seller_amount, min_cap))

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=self.MAX_DURATION)
        for b in buyers: b.redeem_and_forfeit(round_id)
        for s in sellers: s.claim_and_withdraw(round_id)

