from collections import namedtuple, OrderedDict
from web3._utils.events import EventLogErrorFlags
from ten.test.dapps.market.player import MarketDappPlayer

Position = namedtuple('Position', 'position_id round_id amount cost_stake cost_usdc')
Redeemed = namedtuple('Redeemed', 'position_id round_id redeemed')
Forfeit = namedtuple('Forfeit', 'position_id round_id forfeit')


class MarketDappBuyer(MarketDappPlayer):
    """The player who participates in the market as a buyer.

    In this case a stake equates to a position. The stake is the USDC cost to buy an amount of TEN tokens, and the
    co-stake amount of TEN that allows the buyer to participate in the sale. The buyer can then redeem a certain amount
    of their stake for TEN at the USDC cost. This may be less than the amount requested depending on the number
    of buyers in the round (if it is over-subscribed)."""

    def __init__(self, test, pk, id, tokens=1000):
        super().__init__(test, pk, id, tokens)
        self.positions = OrderedDict()
        self.redeemed = OrderedDict()
        self.forfeit = OrderedDict()

    def get_total_staked(self, round_id):
        """Return total stakes amounts across all positions for a given round. """
        total_amount = sum(position.amount for _, position in self.positions.items() if position.round_id == round_id)
        total_cost_stake = sum(position.cost_stake for _, position in self.positions.items() if position.round_id == round_id)
        total_cost_usdc = sum(position.cost_usdc for _, position in self.positions.items() if position.round_id == round_id)
        return total_amount, total_cost_stake, total_cost_usdc

    def get_stake_amounts(self, round_id, amount):
        """Get approve amounts for tokens in a stake."""
        self.log.info('%s %d calculating the stakes: ' % (type(self).__name__, self.id))
        self.log.info('  round id:     %d' % round_id)
        self.log.info('  amount:       %.3f' % self.web3.from_wei(amount, 'ether'))
        cost_stake = self.market.contract.functions.quoteCostakeFor(round_id, amount).call()
        cost_usdc = self.market.contract.functions.quoteUsdcFor(round_id, amount).call()
        self.log.info('  cost_stake:   %.3f' % cost_stake)
        self.log.info('  cost_usdc:    %.3f' % cost_usdc)
        return cost_stake, cost_usdc

    def approve_and_stake(self, round_id, amount, expect_fail=False):
        """Approve ten and usdc stakes to buy a given amount of ten, and place the stake."""
        cost_stake, cost_usdc = self.approve_stakes(round_id, amount)
        tx_receipt, position_id = self.make_stake(round_id, amount, expect_fail)
        self.positions[position_id] = Position(position_id, round_id, amount, cost_stake, cost_usdc)
        return position_id

    def approve_stakes(self, round_id, amount):
        """Approve ten and usdc stakes to buy a given amount of ten."""
        cost_stake, cost_usdc = self.get_stake_amounts(round_id, amount)
        self.approve_ten_token(cost_stake)
        self.approve_usdc_token(cost_usdc)
        return cost_stake, cost_usdc

    def make_stake(self, round_id, amount, expect_fail=False):
        """Call to buy the requested amount of protected ten tokens."""
        self.log.info('%s %d buying protected tokens: ' % (type(self).__name__, self.id))
        self.log.info('  round id: %d' % round_id)
        self.log.info('  amount:   %.3f' % self.web3.from_wei(amount, 'ether'))
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.buyProtectedTokens(round_id, amount),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False, expect_fail=expect_fail)
        tx_log = self.market.contract.events.ProtectedTokensBought().process_receipt(tx_receipt, EventLogErrorFlags.Discard)[0]
        position_id = tx_log['args']['positionId']
        return tx_receipt, position_id

    def redeem_stake(self, round_id, position_id, amount):
        """Redeem an amount of the stake."""
        self.log.info('%s %d redeeming protected tokens: ' % (type(self).__name__, self.id))
        self.log.info('  round id: %d' % round_id)
        self.log.info('  posn id:  %d' % position_id)
        self.log.info('  amount:   %.3f' % self.web3.from_wei(amount, 'ether'))
        self.log.info('  amount:   %d WEI' % amount)
        redeemed = Redeemed(position_id, round_id, amount)
        tx_recp = self.network.transact(self.test, self.web3,
                                        self.market.contract.functions.redeemProtectedTokens(round_id, position_id, amount),
                                        self.account, self.market.GAS_LIMIT, persist_nonce=False)
        if tx_recp.status == 1:
            if position_id in self.redeemed.keys(): self.redeemed[position_id].append(redeemed)
            else: self.redeemed[position_id] = [redeemed]
        return tx_recp

    def forfeit_stake(self, round_id, position_id, amount):
        """Forfeit an amount of the stake."""
        self.log.info('%s %d forfeiting protected tokens: ' % (type(self).__name__, self.id))
        self.log.info('  round id: %d' % round_id)
        self.log.info('  posn id:  %d' % position_id)
        self.log.info('  amount:   %.3f' % self.web3.from_wei(amount, 'ether'))
        self.log.info('  amount:   %d WEI' % amount)
        forfeit = Forfeit(position_id, round_id, amount)
        tx_recp = self.network.transact(self.test, self.web3,
                                        self.market.contract.functions.forfeitProtectedTokens(round_id, position_id, amount),
                                        self.account, self.market.GAS_LIMIT, persist_nonce=False)
        if tx_recp.status == 1:
            if position_id in self.forfeit.keys(): self.forfeit[position_id].append(forfeit)
            else: self.forfeit[position_id] = [forfeit]
        return tx_recp

    def redeem_and_forfeit(self, round_id):
        """Redeem all stakes for a given round. """
        for position_id, position in self.positions.items():
            if position.round_id == round_id:
                redeemable = self.get_redeemable_for_stake(position_id)
                self.redeem_stake(round_id, position_id, redeemable)
                if (position.amount - redeemable) > 0:
                    self.forfeit_stake(round_id, position_id, (position.amount - redeemable))

    def get_redeemable_for_stake(self, position_id):
        """Get the amount of redeemable tokens for a stake."""
        self.log.info('%s %d getting redeemable ten tokens: ' % (type(self).__name__, self.id))
        self.log.info('  posn id: %d' % position_id)
        amount = self.market.contract.functions.redeemableTen(position_id).call()
        return amount

    def to_log(self):
        """Log out a summary of the buyer details. """
        self.log.info('%s %d buyer details: ' % (type(self).__name__, self.id))
        for position_id, position in self.positions.items():
            self.log.info('  round id:     %d' % position.round_id)
            self.log.info('  posn id:      %d' % position_id)
            self.log.info('  amount:       %.3f' % self.web3.from_wei(position.amount, 'ether'))
            self.log.info('  cost_stake:   %.3f' % self.web3.from_wei(position.cost_stake, 'ether'))
            self.log.info('  cost_usdc:    %.3f' % self.web3.from_wei(position.cost_usdc, 'ether'))
            self.log.info('  forfeit:      %.3f' % self.web3.from_wei(self.total_forfeit(position.round_id), 'ether'))
            self.log.info('  redeemed:     %.3f' % self.web3.from_wei(self.total_redeemed(position.round_id), 'ether'))

    def total_redeemed(self, round_id):
        """Returned the total redeemed for this round. """
        return sum([t.redeemed for k, v in self.redeemed.items() for t in v if t.round_id == round_id])

    def total_forfeit(self, round_id):
        """Returned the total forfeit for this round. """
        return sum([t.forfeit for k, v in self.forfeit.items() for t in v if t.round_id == round_id])