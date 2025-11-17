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
