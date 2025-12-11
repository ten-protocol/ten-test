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
        duration = random.randint(60, self.MAX_DURATION)
        deadline = int(admin.web3.eth.get_block("latest").timestamp) + duration
        price = admin.web3.to_wei(random.randint(100,190)/100, 'ether')
        beta = admin.web3.to_wei(random.randint(10,100)/100, 'ether') * 10 ** 9
        ten_cap = admin.web3.to_wei(cap, 'ether')
        min_usdc = admin.web3.to_wei(min_cap, 'ether')
        tax_percent = 200
        _, round_id = admin.create_round(deadline, price, beta, ten_cap, min_usdc, tax_percent)

        sellers = []
        seller_amount = 0
        while seller_amount < cap:
            amount = random.randint(500,1000)
            seller = MarketDappSeller(self, id=len(sellers)+1, ten=2*amount, usdc=2*amount)
            seller.approve_and_deposit(round_id, seller.web3.to_wei(amount, 'ether'))
            sellers.append(seller)
            seller_amount += amount
        self.log.info('Total sellers deposits is %d for cap %d' % (seller_amount, cap))

        buyers = []
        buyer_amount = 0
        while buyer_amount < min_cap:
            amount = random.randint(500,900)
            buyer = MarketDappBuyer(self, id=len(buyers)+1, ten=2*amount, usdc=2*amount)
            self.wait(1.0)
            buyer.approve_and_stake(round_id, buyer.web3.to_wei(amount, 'ether'))
            buyers.append(buyer)
            buyer_amount += amount
        self.log.info('Total buyers stakes is %d for min cap %d' % (buyer_amount, min_cap))

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=self.MAX_DURATION)
        admin.freeze_sellers(round_id)
        for b in buyers: b.redeem_and_forfeit(round_id)
        for s in sellers: s.claim_and_withdraw(round_id)

        self.log.info('')
        self.log.info('Buyer and seller details ...')
        for b in buyers: b.to_log()
        for s in sellers: s.to_log(round_id)
        self.log.info('')

        sellers_nft_balance = sum([s.nft_balance(round_id) for s in sellers])
        sellers_ten_withdrawn = sum([s.get_unused_ten_withdrawn(round_id) for s in sellers])
        sellers_sold = sellers_nft_balance - sellers_ten_withdrawn
        buyers_redeemed = sum([b.total_redeemed(round_id) for b in buyers])
        buyers_forfeit = sum([b.total_forfeit(round_id) for b in buyers])
        self.log.info('cap:                   %s' % cap)
        self.log.info('min cap:               %s' % min_cap)
        self.log.info('buyers_amount:         %s' % admin.web3.to_wei(buyer_amount, 'ether'))
        self.log.info('sellers:               %s' % admin.web3.to_wei(seller_amount, 'ether'))
        self.log.info('sellers_nft_balance:   %s' % sellers_nft_balance)   # how much they were willing to sell
        self.log.info('sellers_ten_withdrawn: %s' % sellers_ten_withdrawn) # how much they claimed back
        self.log.info('sellers_sold:          %s' % sellers_sold)          # how much they actually sold
        self.log.info('buyers_redeemed:       %s' % buyers_redeemed)
        self.log.info('buyers_forfeit:        %s' % buyers_forfeit)

        expected_ten = admin.web3.to_wei(cap, 'ether')
        expected_forfeit = 0
        if buyer_amount < cap: expected_ten = admin.web3.to_wei(buyer_amount, 'ether')
        if buyer_amount > cap: expected_forfeit = admin.web3.to_wei(buyer_amount - cap, 'ether')
        self.log.info('expected_ten:          %s' % expected_ten)
        self.log.info('expected_forfeit:      %s' % expected_forfeit)

        self.assertTrue(sum([s.nft_balance(round_id) for s in sellers]) == admin.web3.to_wei(seller_amount, 'ether'),
                        assertMessage='Seller amount should be sum of the ntf balances')

        self.assertTrue(abs(sellers_sold - buyers_redeemed) < 7500,
                        assertMessage='Seller amount sold should be equal to the buyer redeemed')

        self.assertTrue(abs(expected_ten - buyers_redeemed) < 7500, assertMessage='Expected ten should be buyer redeemed')
        self.assertTrue(abs(expected_forfeit - buyers_forfeit) < 7500, assertMessage='Expected forfeit should be buyer redeemed')

