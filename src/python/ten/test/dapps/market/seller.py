from ten.test.dapps.market.player import MarketDappPlayer
from ten.test.contracts.market import SellerNFT


class MarketDappSeller(MarketDappPlayer):
    """The player who participates in the market as a seller.

    In this case a deposit is an agreement to sell a certain amount of ten tokens. The seller receipt is an NFT
    which details for a given round how much a seller has agreed to sell. Sellers can then claim a certain amount of
    USDC in exchange for up to the amount they agreed to sell, depending on whether the round was over subscribed with
    sellers.
    """

    def __init__(self, test, pk, id, tokens=1000):
        super().__init__(test, pk, id, tokens)
        self.sellerNFT = SellerNFT(self, self.web3, self.get_nft())

    def get_nft(self):
        """Return the seller NFT address."""
        return self.market.contract.functions.getSellerNFT().call()

    def nft_balance(self, round_id):
        """Return the seller deposited balance for a given round. """
        return self.sellerNFT.contract.functions.balanceOf(self.address, round_id).call()

    def claimable_usdc(self, round_id):
        """Return how much a seller can claim in usdc from their deposited amount. """
        return self.market.contract.functions.claimableSellerUSDC(round_id, self.address).call()

    def claimable_ten(self, round_id):
        """Return how much a seller can claim in ten from their deposited amount. """
        return self.market.contract.functions.unusedTenClaimable(round_id, self.address).call()

    def approve_and_deposit(self, round_id, amount):
        """Approve and deposit the tokens. """
        self.approve_ten_tokens(amount)
        return self.deposit_ten_tokens(round_id, amount)

    def approve_ten_tokens(self, amount):
        """Approve the market contract to transfer seller tokens."""
        self.approve_ten_token(amount)

    def deposit_ten_tokens(self, round_id, amount):
        """Deposit ten tokens in a given round. """
        self.log.info('%s %d depositing tokens: ' % (type(self).__name__, self.id))
        self.log.info('  round id: %d' % round_id)
        self.log.info('  amount:   %.3f' % self.web3.from_wei(amount, 'ether'))
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.depositSellerTen(round_id, amount),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def claim_and_withdraw(self, round_id):
        """Claim and withdraw the usdc amount and unused ten tokens."""
        self.claim_usdc(round_id)
        self.withdraw_unused_ten(round_id, self.claimable_ten(round_id))

    def claim_usdc(self, round_id):
        """Claim the usdc for this round. """
        self.log.info('%s %d claiming usdc: ' % (type(self).__name__, self.id))
        self.log.info('  round id: %d' % round_id)
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.claimSellerUSDC(round_id),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def withdraw_unused_ten(self, round_id, amount, expect_fail=False):
        """Withdraw and amount of unused ten tokens for this round. """
        self.log.info('%s %d withdrawing unused tokens: ' % (type(self).__name__, self.id))
        self.log.info('  round id: %d' % round_id)
        self.log.info('  amount:   %.3f' % self.web3.from_wei(amount, 'ether'))
        self.log.info('  amount:   %d WEI' % amount)
        if amount > 0:
            tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.withdrawSellerUnusedTen(round_id, amount),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False, expect_fail=expect_fail)
            return tx_receipt