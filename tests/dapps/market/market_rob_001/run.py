import random
from ten.test.basetest import TenNetworkTest
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        admin = MarketDappAdmin(self)
        admin.increase_evm_time(duration=120)
        self.run_round(admin)

    def run_round(self, admin):
        duration = random.randint(20, 120) # max duration 120 secs
        deadline = int(admin.web3.eth.get_block("latest").timestamp) + duration
        price = admin.web3.to_wei(random.randint(100,190)/100, 'ether')
        beta = admin.web3.to_wei(random.randint(10,100)/100, 'ether') * 10 ** 9
        ten_cap = admin.web3.to_wei(random.randint(1000,4000), 'ether')
        min_usdc = admin.web3.to_wei(random.randint(1000,3500), 'ether')
        _, round_id = admin.create_round(deadline, price, beta, ten_cap, 0, min_usdc)

        # round deadline exceeds and sellers are frozen
        admin.increase_evm_time(duration=120)

