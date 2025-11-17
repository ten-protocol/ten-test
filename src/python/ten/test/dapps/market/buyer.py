from web3._utils.events import EventLogErrorFlags
from ten.test.dapps.market.player import MarketDappPlayer


class MarketDappBuyer(MarketDappPlayer):
    """The player who participates in the market as a buyer."""

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
