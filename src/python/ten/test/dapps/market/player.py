from ten.test.contracts.market import MarketPlace
from ten.test.contracts.market import TestUSDC, TestTEN


class MarketDappPlayer():
    """The base player who participates in the market as a buyer, seller or admin."""

    def __init__(self, test, pk):
        self.test = test
        self.log = test.log
        self.network = test.get_network_connection()
        self.web3, self.account = self.network.connect(test, pk)
        self.address = self.account.address
        self.market = MarketPlace(self, self.web3)
        self.ten = TestTEN(self, self.web3)
        self.usdc = TestUSDC(self, self.web3)
        self.mint_token(self.ten, 'ten')
        self.mint_token(self.usdc, 'usdc')

    def get_ten_token(self):
        """Return the ten token address."""
        return self.market.contract.functions.getTenToken().call()

    def get_position_contract(self):
        """Return the position contract address."""
        return self.market.contract.functions.getPositionContract().call()

    def get_usdc_vault(self):
        """Return the address of the usdc vault."""
        return self.market.contract.functions.getUsdcVault().call()

    def get_proceeds_vault(self):
        """Return the address of the proceeds vault."""
        return self.market.contract.functions.getProceedsVault().call()

    def mint_token(self, token, name, threshold=1000):
        """Mint a token if below a given threshold. """
        balance = token.contract.functions.balanceOf(self.address).call()
        ceiling = self.web3.to_wei(threshold, 'ether')
        if balance < ceiling:
            amount = ceiling-balance
            self.log.info('%s topping up %s token balance' % (type(self).__name__, name))
            self.log.info('  balance = %d ', self.web3.from_wei(balance, 'ether'))
            self.log.info('  ceiling = %d ', self.web3.from_wei(ceiling, 'ether'))
            self.log.info('  amount = %d ', self.web3.from_wei(amount, 'ether'))
            self.log.info('  token = %s ', token.address)
            self.network.transact(self.test, self.web3,
                                  token.contract.functions.mint(self.address, amount),
                                  self.account, token.GAS_LIMIT, persist_nonce=False)

    def ten_balance(self):
        """Return token balance for ten."""
        return self.ten.contract.functions.balanceOf(self.address).call()

    def usdc_balance(self):
        """Return token balance for usdc."""
        return self.usdc.contract.functions.balanceOf(self.address).call()

    def get_token_balances(self, log=False):
        ten_balance = self.ten_balance()
        usdc_balance = self.usdc_balance()
        if log:
            self.log.info('%s retrieving token balances' % type(self).__name__)
            self.log.info('  ten balance  = %d ', self.web3.from_wei(ten_balance, 'ether'))
            self.log.info('  usdc balance = %d ', self.web3.from_wei(usdc_balance, 'ether'))
        return ten_balance, usdc_balance

    def approve_ten_token(self, amount):
        """Call to approve the market contract to spend a given amount of ten."""
        self.log.info('%s approving market to spend TEN token: ' % type(self).__name__)
        self.log.info('  amount:  %d' % self.web3.from_wei(amount, 'ether'))
        self.network.transact(self.test, self.web3,
                              self.ten.contract.functions.approve(self.market.address, amount),
                              self.account, self.ten.GAS_LIMIT, persist_nonce=False)

    def approve_usdc_token(self, amount):
        """Call to approve the market contract to spend a given amount of usdc."""
        self.log.info('%s approving market to spend USDC token: ' % type(self).__name__)
        self.log.info('  amount:  %d' % self.web3.from_wei(amount, 'ether'))
        self.network.transact(self.test, self.web3,
                              self.usdc.contract.functions.approve(self.market.address, amount),
                              self.account, self.usdc.GAS_LIMIT, persist_nonce=False)
