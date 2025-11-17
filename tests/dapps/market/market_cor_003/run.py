from ten.test.contracts.market import MarketPlace
from ten.test.contracts.market import TestUSDC, TestTEN
from ten.test.dapps.market.markettest import MarketDappTest


class PySysTest(MarketDappTest):

    def execute(self):
        # connect account 1 to the network
        web3, account = self.network.connect_account1(self)

        # get a reference to the contracts, and mint tokens for account 1
        market = MarketPlace(self, web3)
        ten = TestTEN(self, self.web3_deployer)
        usdc = TestUSDC(self, self.web3_deployer)

        self.network.transact(self, web3, ten.contract.functions.mint(account.address, 100), account, ten.GAS_LIMIT, persist_nonce=False)
        self.network.transact(self, web3, usdc.contract.functions.mint(account.address, 100), account, usdc.GAS_LIMIT, persist_nonce=False)
        self.network.transact(self, usdc.contract.functions.approve(account.address, 100))
        ten_balance_before = ten.contract.functions.balanceOf(account.address).call()
        usdc_balance_before = usdc.contract.functions.balanceOf(account.address).call()
        self.log.info('  TEN balance before = %d ', ten_balance_before)
        self.log.info('  USDC balance before = %d ', usdc_balance_before)

        # create the default round
        tx_receipt, id = self.create_default_round(market, self.network, self.web3_deployer, self.account_deploy, duration=60)

        # account 1 buys into the market
        self.network.transact(self, web3, market.contract.functions.buyProtectedTokens(id, 10), account, usdc.GAS_LIMIT, persist_nonce=False)
        ten_balance_after = ten.contract.functions.balanceOf(account.address).call()
        usdc_balance_after = usdc.contract.functions.balanceOf(account.address).call()
        self.log.info('  TEN balance after  = %d ', ten_balance_after)
        self.log.info('  USDC balance after  = %d ', usdc_balance_after)

        self.increase_evm_time(duration=60)

