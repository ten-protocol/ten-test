from decimal import Decimal
from ten.test.dapps.market.round import Round
from ten.test.utils.properties import Properties
from ten.test.dapps.market.player import MarketDappPlayer


class MarketDappAdmin(MarketDappPlayer):
    """The player with an operational role on the market contracts."""

    def __init__(self, test):
        super().__init__(test, Properties().fundacntpk())

    def create_round(self, deadline, price, beta, ten_cap, max_usdc, min_usdc):
        """Create a new round."""
        self.log.info('Making new round: ')
        self.log.info('  deadline: %d' % deadline)
        self.log.info('  price:    %d' % price)
        self.log.info('  beta:     %d' % beta)
        self.log.info('  tenCap:   %d' % ten_cap)
        self.log.info('  maxUSDC:  %d' % max_usdc)
        self.log.info('  minUSDC:  %d' % min_usdc)
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.createRound(deadline, price, beta, ten_cap, max_usdc, min_usdc),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        tx_log = self.market.contract.events.RoundCreated().process_receipt(tx_receipt)[0]
        id = tx_log['args']['id']
        return tx_receipt, id

    def create_default_round(self,duration=60):
        """Create a round with price 1.1 USD, co-stake 25%, capped at 1000 with min of 500."""
        deadline = int(self.web3.eth.get_block("latest").timestamp) + duration
        price = self.web3.to_wei(1.1, 'ether')
        beta = self.to_ray(0.25)
        ten_cap = self.web3.to_wei(1000, 'ether')
        min_usdc = 500 * self.web3.to_wei(1, 'ether')
        return self.create_round(deadline, price, beta, ten_cap, 0, min_usdc)

    def freeze_sellers(self, round_id):
        self.log.info('Freezing sellers for round: ')
        self.log.info('  round id: %d' % round_id)
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.freezeSellers(round_id),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def cancel_if_under_min(self, round_id):
        self.log.info('Cancelling for round: ')
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
