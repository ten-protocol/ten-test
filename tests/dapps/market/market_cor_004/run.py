from ten.test.contracts.market import MarketPlace
from ten.test.contracts.market import TestUSDC, TestTEN
from ten.test.dapps.market.markettest import MarketDappTest


class PySysTest(MarketDappTest):

    def execute(self):
        # connect account 1 to the network
        web3_b1, account_b1 = self.network.connect_account1(self)

        # get a reference to the contracts
        market = MarketPlace(self, web3_b1)
        ten = TestTEN(self, self.web3_deployer)
        usdc = TestUSDC(self, self.web3_deployer)

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 500)
        tx_receipt, id = self.create_default_round(market, self.network, self.web3_deployer, self.account_deploy, duration=60)

        # buyer 1 is going to go for 100 tokens
        self.mint_if_needed(web3_b1, account_b1, ten)
        self.mint_if_needed(web3_b1, account_b1, usdc)

        buyer1_amount = web3_b1.to_wei(100, 'ether')
        cost_stake = market.contract.functions.quoteCostakeFor(id, buyer1_amount).call()
        cost_usdc = market.contract.functions.quoteUsdcFor(id, buyer1_amount).call()
        self.network.transact(self, web3_b1, ten.contract.functions.approve(market.address, cost_stake), account_b1, usdc.GAS_LIMIT, persist_nonce=False)
        self.network.transact(self, web3_b1, usdc.contract.functions.approve(market.address, cost_usdc), account_b1, usdc.GAS_LIMIT, persist_nonce=False)

        # account 1 buys into the market
        tx_receipt, position_id = self.buy_protected_tokens(market, web3_b1, account_b1, buyer1_amount, id)
        self.log.info('Position created with id = %d' % position_id)

        # close the round with it never trading out
        self.increase_evm_time(duration=60)
        is_active = market.contract.functions.isActive(id).call()
        self.log.info('Latest round %d is_active = %s' % (id, is_active))

        # forfeit the tokens
        self.forfeit_protected_tokens(market, web3_b1, account_b1, id, position_id, buyer1_amount)
        ten_balance_forfeit = ten.contract.functions.balanceOf(account_b1.address).call()
        usdc_balance_forfeit = usdc.contract.functions.balanceOf(account_b1.address).call()
        self.log.info('  TEN balance on forfeit  = %d ', ten_balance_forfeit)
        self.log.info('  USDC balance on forfeit  = %d ', usdc_balance_forfeit)

        # check the buyers balances are returned to the original values
        self.assertTrue(ten_balance_before == ten_balance_forfeit, assertMessage='TEN should be back to original')
        self.assertTrue(usdc_balance_before == usdc_balance_forfeit, assertMessage='USDC should be back to original')

