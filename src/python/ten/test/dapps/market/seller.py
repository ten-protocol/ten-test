from ten.test.dapps.market.player import MarketDappPlayer
from ten.test.contracts.market import SellerNFT


class MarketDappSeller(MarketDappPlayer):
    """The player who participates in the market as a seller."""

    def __init__(self, test, pk):
        super().__init__(test, pk)
        self.sellerNFT = SellerNFT(self, self.web3, self.get_seller_nft())

    def get_seller_nft(self):
        """Return the seller NFT address."""
        return self.market.contract.functions.getSellerNFT().call()

    def seller_nft_balance(self, round_id):
        """Return the seller deposited balance for a given round. """
        return self.sellerNFT.contract.functions.balanceOf(self.address, round_id).call()

    def claimable_seller_usdc(self, round_id):
        """Return how much a seller can claim in usdc from their deposited amount. """
        return self.market.contract.functions.claimableSellerUSDC(round_id, self.address).call()

    def unused_ten_claimable(self, round_id):
        """Return how much a seller can claim in ten from their deposited amount. """
        return self.market.contract.functions.unusedTenClaimable(round_id, self.address).call()

    def approve_deposit(self, amount):
        """Approve the market contract to transfer seller tokens."""
        self.approve_ten_token(amount)

    def deposit_ten_tokens(self, round_id, amount):
        """Deposit ten tokens in a given round. """
        self.log.info('Seller depositing tokens: ')
        self.log.info('  round id: %d' % round_id)
        self.log.info('  amount:   %d' % self.web3.from_wei(amount, 'ether'))
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.depositSellerTen(round_id, amount),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt

    def withdraw_unused_ten(self, round_id, amount):
        """Withdraw under ten tokens. """
        self.log.info('Seller withdrawing unused tokens: ')
        self.log.info('  round id: %d' % round_id)
        self.log.info('  amount:   %d' % self.web3.from_wei(amount, 'ether'))
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.withdrawSellerUnusedTen(round_id, amount),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt