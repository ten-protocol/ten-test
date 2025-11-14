from pysys.constants import FAILED
from ten.test.utils.properties import Properties
from ten.test.contracts.market import MarketPlace
from ten.test.dapps.market.markettest import MarketDappTest, Round


class PySysTest(MarketDappTest):

    def execute(self):
        props = Properties()

        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=props.market_deployer_pk())

        # get the market place contract and check there is code
        market = MarketPlace(self, web3)

        self.log.info('Checking there is contract code at marketplace address %s' % market.address)
        code = web3.eth.get_code(market.address)
        self.log.info("Contract bytecode length: %d", len(code))
        if code == b'' or code == '0x' or len(code) == 0:
            self.log.info("No contract code at that address — address wrong or contract not deployed.")
            self.addOutcome(FAILED, outcomeReason='No code at address', abortOnError=True)

        # get the latest round id
        round_id_before = market.contract.functions.latestRoundId().call()
        self.log.info('Latest round id is %d' % round_id_before)

        # create a new round
        deadline = int(web3.eth.get_block("latest").timestamp) + 60
        price = web3.to_wei(1, 'ether')
        beta = self.to_ray(0.25)
        tenCap = web3.to_wei(1000, 'ether')
        maxUSDC = 0
        minUSDC = 500 * web3.to_wei(1, 'ether')
        self.create_round(market, network, web3, account, deadline, price, beta, tenCap, maxUSDC, minUSDC)

        # get the latest round id
        round_id_after = market.contract.functions.latestRoundId().call()
        self.log.info('Latest round id is %d' % round_id_after)
        self.assertTrue(round_id_after == round_id_before + 1, assertMessage='Round id should increase by one')

        is_active = market.contract.functions.isActive(round_id_after).call()
        self.log.info('Latest round %d is_active = %s' % (round_id_after, is_active))
        self.assertTrue(is_active == True, assertMessage='Round should be active')

        get_round = market.contract.functions.getRound(round_id_after).call()
        round = Round(*get_round)
        self.assertTrue(round.deadline == deadline, assertMessage='Round deadline should match')
        self.assertTrue(round.priceMicro == price, assertMessage='Round priceMicro should match')
        self.assertTrue(round.coStakeRatio == beta, assertMessage='Round coStakeRatio should match')
        self.assertTrue(round.tenCap == tenCap, assertMessage='Round tenCap should match')
        self.assertTrue(round.minCollectedUSDC == minUSDC, assertMessage='Round minCollectedUSDC should match')

        # increase time so the round becomes inactive
        self.log.info('Block time is %d ' % web3.eth.get_block("latest").timestamp)
        web3.provider.make_request("evm_increaseTime",[60])
        web3.provider.make_request("evm_mine", [])
        self.log.info('Block time is %d ' % web3.eth.get_block("latest").timestamp)

        is_active = market.contract.functions.isActive(round_id_after).call()
        self.log.info('Latest round %d is_active = %s' % (round_id_after, is_active))
        self.assertTrue(is_active == False, assertMessage='Round should be inactive')


    def create_round(self, market, network, web3, account, deadline, price, beta, tenCap, maxUSDC, minUSDC):
        target = market.contract.functions.createRound(deadline, price, beta, tenCap, maxUSDC, minUSDC)
        tx_receipt = network.transact(self, web3, target, account, market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt