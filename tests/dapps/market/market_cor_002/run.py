from pysys.constants import FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)

        self.log.info('Checking there is contract code at marketplace address %s' % admin.market.address)
        code = admin.web3.eth.get_code(admin.market.address)
        self.log.info("Contract bytecode length: %d", len(code))
        if code == b'' or code == '0x' or len(code) == 0:
            self.log.info("No contract code at that address — address wrong or contract not deployed.")
            self.addOutcome(FAILED, outcomeReason='No code at address', abortOnError=True)

        # get the latest round id
        round_id_before = admin.latest_round_id()
        self.log.info('Latest round id is %d' % round_id_before)

        # create a new round
        deadline = admin.get_block_time() + 60
        price = admin.web3.to_wei(1, 'ether')
        beta = admin.to_ray(0.25)
        ten_cap = admin.web3.to_wei(1000, 'ether')
        min_usdc = 500 * admin.web3.to_wei(1, 'ether')
        tx_receipt, id = admin.create_round(deadline, price, beta, ten_cap, min_usdc)
        self.log.info('Transaction receipt shows round id is %d' % id)

        # get the latest round id
        round_id_after = admin.latest_round_id()
        self.log.info('Call to latestRoundId shows round id is %d' % round_id_after)
        self.assertTrue(round_id_after == round_id_before + 1, assertMessage='Round id should increase by one')
        self.assertTrue(round_id_after == id, assertMessage='Transaction receipt and call to latest should match')

        # check the round is active
        is_active = admin.is_active(round_id_after)
        self.log.info('Latest round %d is_active = %s' % (round_id_after, is_active))
        self.assertTrue(is_active == True, assertMessage='Round should be active')

        # check the round details
        round = admin.get_round(round_id_after)
        self.assertTrue(round.deadline == deadline, assertMessage='Round deadline should match')
        self.assertTrue(round.priceMicro == price, assertMessage='Round priceMicro should match')
        self.assertTrue(round.coStakeRatio == beta, assertMessage='Round coStakeRatio should match')
        self.assertTrue(round.tenCap == ten_cap, assertMessage='Round tenCap should match')
        self.assertTrue(round.minCollectedUSDC == min_usdc, assertMessage='Round minCollectedUSDC should match')

        # increase evm time so the round becomes inactive
        self.log.info('Current block time is %d ' % admin.get_block_time())
        admin.increase_evm_time(60)
        self.log.info('Current block time is %d ' % admin.get_block_time())

        is_active = admin.is_active(round_id_after)
        self.log.info('Latest round %d is_active = %s' % (round_id_after, is_active))
        self.assertTrue(is_active == False, assertMessage='Round should be inactive')
