from collections import namedtuple
from ten.test.contracts.market import MarketPlace
from ten.test.contracts.market import TestUSDC, TestTEN

Balance = namedtuple('Balance', 'ten usdc')


class MarketDappPlayer():
    """The base player who participates in the market as a buyer, seller or admin. """

    def __init__(self, test, pk, id, ten=1000, usdc=1000, locked=False):
        self.id = id
        self.test = test
        self.log = test.log
        self.balances = {}
        self.network = test.get_network_connection()
        self.web3, self.account = self.network.connect(test, pk)
        self.address = self.account.address
        self.market = MarketPlace(test, self.web3)
        self.ten = TestTEN(test, self.web3)
        self.usdc = TestUSDC(test, self.web3)
        if ten > 0: self.mint_token(self.ten, 'ten', ten, locked=locked)
        if usdc > 0: self.mint_token(self.usdc, 'usdc', usdc)

    def get_position_contract(self):
        """Return the position contract address."""
        return self.market.contract.functions.getPositionContract().call()

    def get_usdc_vault(self):
        """Return the address of the usdc vault."""
        return self.market.contract.functions.getUsdcVault().call()

    def get_proceeds_vault(self):
        """Return the address of the proceeds vault."""
        return self.market.contract.functions.getProceedsVault().call()

    def mint_token(self, token, name, amount, locked=False):
        """Mint a token if below a given threshold. """
        amount = self.web3.to_wei(amount, 'ether')
        balance = token.contract.functions.balanceOf(self.address).call()
        self.log.info('%s %d topping up %s token balance' % (type(self).__name__, self.id, name))
        self.log.info('  balance = %d ', self.web3.from_wei(balance, 'ether'))
        self.log.info('  amount = %d ', self.web3.from_wei(amount, 'ether'))
        self.log.info('  token = %s ', token.address)
        self.log.info('  locked = %s ', locked)
        self.network.transact(self.test, self.web3, token.contract.functions.mint(self.address, amount),
                                  self.account, token.GAS_LIMIT, persist_nonce=False)
        if locked:
            self.network.transact(self.test, self.web3, token.contract.functions.setLock(self.address, True),
                                      self.account, token.GAS_LIMIT, persist_nonce=False)

        balance = token.contract.functions.balanceOf(self.address).call()
        self.log.info('%s %d topped up %s token balance' % (type(self).__name__, self.id, name))
        self.log.info('  new balance = %d ', self.web3.from_wei(balance, 'ether'))

    def ten_balance(self):
        """Return token balance for ten."""
        return self.ten.contract.functions.balanceOf(self.address).call()

    def usdc_balance(self):
        """Return token balance for usdc."""
        return self.usdc.contract.functions.balanceOf(self.address).call()

    def token_balances(self):
        """Return the ten and usdc token balances. """
        return Balance(self.ten_balance(), self.usdc_balance())

    def store_balances(self, key):
        """Get, store and return the ten and usdc token balances. """
        self.balances[key] = self.token_balances()
        return self.balances[key]

    def log_stored_balances(self, delta=None):
        """Log the ten and usdc token balances, and the delta between two stored points, returning the delta. """
        self.log.info('%s %d token balances (ten,usdc): ' % (type(self).__name__, self.id))
        for k in self.balances:
            ten = self.web3.from_wei(self.balances[k].ten, 'ether')
            usdc = self.web3.from_wei(self.balances[k].usdc, 'ether')
            self.log.info('  %s: %.3f, %.3f' % (k, ten, usdc))
        if delta is not None:
            dten = self.balances[delta[0]].ten - self.balances[delta[1]].ten
            dusdc = self.balances[delta[0]].usdc - self.balances[delta[1]].usdc
            self.log.info('  delta: %s%.3f, %s%.3f' % ('-' if dten<0 else '',  self.web3.from_wei(abs(dten), 'ether'),
                                                   '-' if dusdc<0 else '',  self.web3.from_wei(abs(dusdc), 'ether')))
            return Balance(dten, dusdc)
        else: return None, None

    def approve_ten_token(self, amount):
        """Call to approve the market contract to spend a given amount of ten."""
        self.log.info('%s %s approving market to spend TEN token: ' % (type(self).__name__, self.id))
        self.log.info('  amount:  %.3f' % self.web3.from_wei(amount, 'ether'))
        self.network.transact(self.test, self.web3,
                              self.ten.contract.functions.approve(self.market.address, amount),
                              self.account, self.ten.GAS_LIMIT, persist_nonce=False)

    def approve_usdc_token(self, amount):
        """Call to approve the market contract to spend a given amount of usdc."""
        self.log.info('%s %s approving market to spend USDC token: ' % (type(self).__name__, self.id))
        self.log.info('  amount:  %.3f' % self.web3.from_wei(amount, 'ether'))
        self.network.transact(self.test, self.web3,
                              self.usdc.contract.functions.approve(self.market.address, amount),
                              self.account, self.usdc.GAS_LIMIT, persist_nonce=False)
