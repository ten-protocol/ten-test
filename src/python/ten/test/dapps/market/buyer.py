from web3._utils.events import EventLogErrorFlags
from ten.test.contracts.market import MarketPlace
from ten.test.contracts.market import TestUSDC, TestTEN

class MarketDappBuyer():

    def __init__(self, test, pk):
        self.test = test
        self.log = test.log
        self.network = test.get_network_connection()
        self.web3, self.account = self.network.connect(test, pk)
        self.address = self.account.address
        self.market = MarketPlace(self, self.web3)
        self.ten = TestTEN(self, self.web3)
        self.usdc = TestUSDC(self, self.web3)
        self.mint_if_needed(self.ten)
        self.mint_if_needed(self.usdc)

    def mint_if_needed(self, token, threshold=1000):
        """Mint token if below a given threshold. """
        balance = token.contract.functions.balanceOf(self.address).call()
        ceiling = self.web3.to_wei(threshold, 'ether')
        if balance < ceiling:
            amount = ceiling-balance
            self.log.info('Topping up account %s with %d for token %s' % (self.address, amount, token.address))
            self.network.transact(self.test, self.web3,
                                  token.contract.functions.mint(self.address, amount),
                                  self.account, token.GAS_LIMIT, persist_nonce=False)

    def ten_balance(self):
        """Return token balance for ten."""
        return self.ten.contract.functions.balanceOf(self.address).call()

    def usdc_balance(self):
        """Return token balance for usdc."""
        return self.usdc.contract.functions.balanceOf(self.address).call()

    def approve_stakes(self, round_id, amount):
        """Approve stakes to buy a given amount of ten."""
        cost_stake, cost_usdc = self.get_stakes(round_id, amount)
        self.approve_ten_token(cost_stake)
        self.approve_usdc_token(cost_usdc)
        return cost_stake, cost_usdc

    def buy_protected_tokens(self, round_id, amount, expect_fail=False):
        """Call to buy the requested amount of ten."""
        self.log.info('Buying protected tokens: ')
        self.log.info('  round id: %d' % round_id)
        self.log.info('  amount:   %d' % amount)
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.buyProtectedTokens(round_id, amount),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False, expect_fail=expect_fail)
        tx_log = self.market.contract.events.ProtectedTokensBought().process_receipt(tx_receipt, EventLogErrorFlags.Discard)[0]
        position_id = tx_log['args']['positionId']
        return tx_receipt, position_id

    def forfeit_protected_tokens(self, round_id, position_id, amount):
        """Forfeit an amount of the requested tokens."""
        self.log.info('Forfeiting protected tokens: ')
        self.log.info('  round id: %d' % round_id)
        self.log.info('  posn id:  %d' % position_id)
        self.log.info('  amount:   %d' % amount)
        return self.network.transact(self.test, self.web3,
                                     self.market.contract.functions.forfeitProtectedTokens(round_id, position_id, amount),
                                     self.account, self.market.GAS_LIMIT, persist_nonce=False)

    def get_stakes(self, round_id, amount):
        """Convenience call to determine the stake amounts."""
        self.log.info('Calculating the stakes: ')
        self.log.info('  round id: %d' % round_id)
        self.log.info('  amount:   %d' % amount)
        cost_stake = self.market.contract.functions.quoteCostakeFor(round_id, amount).call()
        cost_usdc = self.market.contract.functions.quoteUsdcFor(round_id, amount).call()
        return cost_stake, cost_usdc

    def approve_ten_token(self, amount):
        """Call to approve the market contract to spend a given amount of ten."""
        self.log.info('Approving market to spend TEN token: ')
        self.log.info('  amount:  %d' % amount)
        self.network.transact(self.test, self.web3,
                              self.ten.contract.functions.approve(self.market.address, amount),
                              self.account, self.ten.GAS_LIMIT, persist_nonce=False)

    def approve_usdc_token(self, amount):
        """Call to approve the market contract to spend a given amount of usdc."""
        self.log.info('Approving market to spend USDC token: ')
        self.log.info('  amount:  %d' % amount)
        self.network.transact(self.test, self.web3,
                              self.usdc.contract.functions.approve(self.market.address, amount),
                              self.account, self.usdc.GAS_LIMIT, persist_nonce=False)
