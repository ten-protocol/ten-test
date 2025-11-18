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
        """Return the sellers balance for a given round. """
        return self.sellerNFT.contract.functions.balanceOf(self.address, round_id).call()

    def approve_deposit(self, amount):
        self.approve_ten_token(amount)

    def deposit_ten_tokens(self, round_id, amount):
        self.log.info('Depositing tokens: ')
        self.log.info('  round id: %d' % round_id)
        self.log.info('  amount:   %d' % amount)
        tx_receipt = self.network.transact(self.test, self.web3,
                                           self.market.contract.functions.depositSellerTen(round_id, amount),
                                           self.account, self.market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt