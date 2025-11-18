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
        
    def to_log(self, test):
        test.log.info(' deadline = %s' % self.deadline)
        test.log.info(' quoteLastUpdate = %s' % self.quoteLastUpdate)
        test.log.info(' priceMicro = %s' % self.priceMicro)
        test.log.info(' coStakeRatio = %s' % self.coStakeRatio)
        test.log.info(' tenCap = %s' % self.tenCap)
        test.log.info(' maxUSDC = %s' % self.maxUSDC)
        test.log.info(' fundedUSDC = %s' % self.fundedUSDC)
        test.log.info(' collectedUSDC = %s' % self.collectedUSDC)
        test.log.info(' claimedUSDC = %s' % self.claimedUSDC)
        test.log.info(' sellersFrozen = %s' % self.sellersFrozen)
        test.log.info(' sellerScale = %s' % self.sellerScale)
        test.log.info(' buyerCoverage = %s' % self.buyerCoverage)
        test.log.info(' totalBuyerTEN = %s' % self.totalBuyerTEN)
        test.log.info(' releasedActiveTEN = %s' % self.releasedActiveTEN)
        test.log.info(' buyerVault = %s' % self.buyerVault)
        test.log.info(' proceedsVault = %s' % self.proceedsVault)
        test.log.info(' minCollectedUSDC = %s' % self.minCollectedUSDC)
        test.log.info(' canceled = %s' % self.canceled)
        test.log.info(' canceledAt = %s' % self.canceledAt)
        
