from decimal import Decimal
from ten.test.utils.properties import Properties
from ten.test.basetest import TenNetworkTest
from web3._utils.events import EventLogErrorFlags


class Round:
    def __init__( self, deadline, quoteLastUpdate, priceMicro, coStakeRatio, tenCap, maxUSDC, fundedUSDC,
                  collectedUSDC, claimedUSDC, sellersFrozen, sellerScale, buyerCoverage, totalBuyerTEN,
                  releasedActiveTEN, buyerVault, proceedsVault, minCollectedUSDC, canceled, canceledAt):
        self.deadline = deadline
        self.quoteLastUpdate = quoteLastUpdate
        self.priceMicro = priceMicro
        self.coStakeRatio = coStakeRatio
        self.tenCap = tenCap
        self.maxUSDC = maxUSDC
        self.fundedUSDC = fundedUSDC
        self.collectedUSDC = collectedUSDC
        self.claimedUSDC = claimedUSDC
        self.sellersFrozen = sellersFrozen
        self.sellerScale = sellerScale
        self.buyerCoverage = buyerCoverage
        self.totalBuyerTEN = totalBuyerTEN
        self.releasedActiveTEN = releasedActiveTEN
        self.buyerVault = buyerVault
        self.proceedsVault = proceedsVault
        self.minCollectedUSDC = minCollectedUSDC
        self.canceled = canceled
        self.canceledAt = canceledAt


class MarketDappTest(TenNetworkTest):

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to ten if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.network = self.get_network_connection()
        self.web3_deployer, self.account_deploy = self.network.connect(self, private_key=Properties().fundacntpk())
        self.align_time()

    def align_time(self):
        """This ensures calling as a client to get the latest block timestamp matches what solidity sees.

        This only works on dev networks like hardhat. Clients calls using web3.eth.get_block("latest").timestamp
        gives the time of the last block executed, whereas in solidity block.timestamp gives the time of the current
        one. If you advance the time but don't mine, these will therefore be out of sync.
        """
        self.web3_deployer.provider.make_request("evm_mine", [])

    def to_ray(self, amount):
        """Convert an amount in RAY."""
        return int(Decimal(amount) * 10 ** 27)

    def increase_evm_time(self, duration=60):
        """Increase the EVM time by a set duration and perform a time sync between node and clients. """
        self.web3_deployer.provider.make_request("evm_increaseTime",[duration])
        self.align_time()

    def get_block_time(self):
        """Get the node timestamp, base on the time of the last execution block. """
        return int(self.web3_deployer.eth.get_block("latest").timestamp)

    def create_round(self, market, network, web3, account, deadline, price, beta, tenCap, maxUSDC, minUSDC):
        """Create a new round."""
        self.log.info('Making new round: ')
        self.log.info('  deadline: %d' % deadline)
        self.log.info('  price:    %d' % price)
        self.log.info('  beta:     %d' % beta)
        self.log.info('  tenCap:   %d' % tenCap)
        self.log.info('  maxUSDC:  %d' % maxUSDC)
        self.log.info('  minUSDC:  %d' % minUSDC)
        target = market.contract.functions.createRound(deadline, price, beta, tenCap, maxUSDC, minUSDC)
        tx_receipt = network.transact(self, web3, target, account, market.GAS_LIMIT, persist_nonce=False)
        tx_log = market.contract.events.RoundCreated().process_receipt(tx_receipt)[0]
        id = tx_log['args']['id']
        return (tx_receipt, id)

    def buy_protected_tokens(self, market, web3, account, amount, round_id):
        """Buy protected tokens."""
        self.log.info('Buying protected tokens: ')
        self.log.info('  round id: %d' % round_id)
        self.log.info('  amount:   %d' % amount)
        target = market.contract.functions.buyProtectedTokens(round_id, amount)
        tx_receipt = self.network.transact(self, web3, target, account, market.GAS_LIMIT, persist_nonce=False)
        tx_log = market.contract.events.ProtectedTokensBought().process_receipt(tx_receipt, EventLogErrorFlags.Discard)[0]
        position_id = tx_log['args']['positionId']
        return (tx_receipt, position_id)

    def forfeit_protected_tokens(self, market, web3, account, round_id, position_id, amount):
        """Forfeit protected tokens."""
        self.log.info('Forfeiting protected tokens: ')
        self.log.info('  round id: %d' % round_id)
        self.log.info('  posn id:  %d' % position_id)
        self.log.info('  amount:   %d' % amount)
        target = market.contract.functions.forfeitProtectedTokens(round_id, position_id, amount)
        return self.network.transact(self, web3, target, account, market.GAS_LIMIT, persist_nonce=False)

    def create_default_round(self, market, network, web3, account, duration=60):
        """Creates a default round with price 1.1 USD, co-stake 25%, capped at 1000 with min of 500."""
        deadline = int(web3.eth.get_block("latest").timestamp) + duration
        price = web3.to_wei(1.1, 'ether')
        beta = self.to_ray(0.25)
        tenCap = web3.to_wei(1000, 'ether')
        minUSDC = 500 * web3.to_wei(1, 'ether')
        return self.create_round(market, network, web3, account, deadline, price, beta, tenCap, 0, minUSDC)

    def mint_if_needed(self, web3, account, token, threshold=1000):
        """Mint some tokens if below a given threshold. """
        balance = token.contract.functions.balanceOf(account.address).call()
        ceiling = web3.to_wei(threshold, 'ether')
        if balance < ceiling:
            amount = ceiling-balance
            self.log.info('Topping up account %s with %d for token %s' % (account.address, amount, token.address))
            self.network.transact(self, web3, token.contract.functions.mint(account.address, amount), account, token.GAS_LIMIT, persist_nonce=False)

