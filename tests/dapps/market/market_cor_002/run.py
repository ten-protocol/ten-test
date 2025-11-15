from pysys.constants import FAILED
from ten.test.utils.properties import Properties
from ten.test.contracts.market import MarketPlace
from ten.test.dapps.market.markettest import MarketDappTest, Round


class PySysTest(MarketDappTest):

    def execute(self):
        # get the market place contract and check there is code
        market = MarketPlace(self, self.web3_deployer)

        self.log.info('Checking there is contract code at marketplace address %s' % market.address)
        code = self.web3_deployer.eth.get_code(market.address)
        self.log.info("Contract bytecode length: %d", len(code))
        if code == b'' or code == '0x' or len(code) == 0:
            self.log.info("No contract code at that address — address wrong or contract not deployed.")
            self.addOutcome(FAILED, outcomeReason='No code at address', abortOnError=True)

        # get the latest round id
        round_id_before = market.contract.functions.latestRoundId().call()
        self.log.info('Latest round id is %d' % round_id_before)

        # create a new round
        node_time = market.contract.functions.latestBlockTime().call()
        client_time = self.get_block_time()
        self.log.info(node_time)
        self.log.info(client_time)

        deadline = self.get_block_time() + 60
        price = self.web3_deployer.to_wei(1, 'ether')
        beta = self.to_ray(0.25)
        tenCap = self.web3_deployer.to_wei(1000, 'ether')
        maxUSDC = 0
        minUSDC = 500 * self.web3_deployer.to_wei(1, 'ether')
        tx_receipt, id = self.create_round(market, self.network, self.web3_deployer, self.account_deploy,
                                           deadline, price, beta, tenCap, maxUSDC, minUSDC)
        self.log.info('Transaction receipt shows round id is %d' % id)

        # get the latest round id
        round_id_after = market.contract.functions.latestRoundId().call()
        self.log.info('Call to latestRoundId shows round id is %d' % round_id_after)
        self.assertTrue(round_id_after == round_id_before + 1, assertMessage='Round id should increase by one')
        self.assertTrue(round_id_after == id, assertMessage='Transaction receipt and call to latest should match')

        is_active = market.contract.functions.isActive(round_id_after).call()
        self.log.info('Latest round %d is_active = %s' % (round_id_after, is_active))
        self.assertTrue(is_active == True, assertMessage='Round should be active')

        round = Round(*market.contract.functions.getRound(round_id_after).call())
        self.assertTrue(round.deadline == deadline, assertMessage='Round deadline should match')
        self.assertTrue(round.priceMicro == price, assertMessage='Round priceMicro should match')
        self.assertTrue(round.coStakeRatio == beta, assertMessage='Round coStakeRatio should match')
        self.assertTrue(round.tenCap == tenCap, assertMessage='Round tenCap should match')
        self.assertTrue(round.minCollectedUSDC == minUSDC, assertMessage='Round minCollectedUSDC should match')

        # increase time so the round becomes inactive
        self.log.info('Current block time is %d ' % self.get_block_time())
        self.increase_evm_time(60)
        self.log.info('Current block time is %d ' % self.get_block_time())

        is_active = market.contract.functions.isActive(round_id_after).call()
        self.log.info('Latest round %d is_active = %s' % (round_id_after, is_active))
        self.assertTrue(is_active == False, assertMessage='Round should be inactive')
