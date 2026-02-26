from decimal import Decimal
from ten.test.dapps.market.round import Round
from ten.test.utils.properties import Properties
from ten.test.dapps.market.player import MarketDappPlayer


class MarketDappAdmin(MarketDappPlayer):
    """The player who participates in the market as an administrator.

    The admin has the operational role to be able to create rounds, cancel rounds and to freeze sellers so that
    the buyers and sellers can claim and sell their tokens. The admin is also used for aligning and increasing times
    in a dev local test network.
    """

    def __init__(self, test):
        super().__init__(test, Properties().fundacntpk(), id=0, ten=0, usdc=0)
        self.log.info('Admin block time is %s' % self.web3.eth.get_block("latest").timestamp)

    def create_round(self, deadline, price, beta, ten_cap, min_usdc, tax_perc, cooldown):
        """Create a new round."""
        self.log.info('%s %s making new round: ' % (type(self).__name__, self.id))
        self.log.info('  deadline: %d' % deadline)
        self.log.info('  price:    %d' % price)
        self.log.info('  beta:     %d' % beta)
        self.log.info('  tenCap:   %d' % self.web3.from_wei(ten_cap, 'ether'))
        self.log.info('  minUSDC:  %d' % self.web3.from_wei(min_usdc, 'ether'))
        self.log.info('  tax:      %d' % tax_perc)
        self.log.info('  cooldown: %d' % cooldown)

        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.createRound(deadline, price, beta, ten_cap, min_usdc, tax_perc, cooldown),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        tx_log = self.market.contract.events.RoundCreated().process_receipt(tx_receipt)[0]
        round_id = tx_log['args']['id']
        return tx_receipt, round_id

    def create_default_round(self, duration=60):
        """Create a round with price 1.1 USD, co-stake 25%, capped at 1000 with min of 550 USDC, 2% tax."""
        deadline = int(self.web3.eth.get_block("latest").timestamp) + duration
        price = self.web3.to_wei(1.1, 'ether')
        beta = self.to_ray(0.25)                       # 25 percent
        ten_cap = self.web3.to_wei(1000, 'ether')      # 1000 tokens
        min_usdc = self.web3.to_wei(550, 'ether')      # 500 tokens at 1.1 USD per token
        tax_perc = 200                                 # 2 percent
        cooldown = 0                                   # forfeit cooldown
        return self.create_round(deadline, price, beta, ten_cap, min_usdc, tax_perc, cooldown)

    def freeze_sellers(self, round_id):
        self.log.info('%s %d freezing sellers for round: ' % (type(self).__name__, self.id))
        self.log.info('  round id: %d' % round_id)
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.freezeSellers(round_id),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def cancel_if_under_min(self, round_id):
        self.log.info('%s %s cancelling round: ' % (type(self).__name__, self.id))
        self.log.info('  round id: %d' % round_id)
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.cancelIfUnderMin(round_id),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def latest_round_id(self):
        """Return the latest round id."""
        return self.market.contract.functions.latestRoundId().call()

    def is_active(self, round_id):
        """Return true if the round is active."""
        return self.market.contract.functions.isActive(round_id).call()

    def get_round(self, round_id):
        """Get the round details."""
        return Round(*self.market.contract.functions.getRound(round_id).call())

    def align_time(self):
        """Ensure client and node times are aligned."""
        self.web3.provider.make_request("evm_mine", [])

    def increase_evm_time(self, duration=60):
        """Increase the EVM time. """
        self.web3.provider.make_request("evm_increaseTime",[duration])
        self.align_time()

    def get_block_time(self):
        """Get the node timestamp, base on the time of the last execution block. """
        return int(self.web3.eth.get_block("latest").timestamp)

    def to_ray(self, amount):
        """Convert an amount to RAY."""
        return int(Decimal(amount) * 10 ** 27)
