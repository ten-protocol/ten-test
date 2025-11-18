from ten.test.dapps.market.player import MarketDappPlayer


class MarketDappSeller(MarketDappPlayer):
    """The player who participates in the market as a seller."""

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