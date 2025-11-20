from pysys.constants import FAILED, PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.dapps.market.buyer import MarketDappBuyer
from ten.test.dapps.market.admin import MarketDappAdmin


class PySysTest(TenNetworkTest):

    def execute(self):
        # the actors in the test
        admin = MarketDappAdmin(self)
        buyer = MarketDappBuyer(self, pk=Properties().account1pk(), id=1)

        # create a default round (price 1.1 USD, co-stake 25%, capped at 1000 with min of 500)
        _, round_id = admin.create_default_round(duration=60)

        # buyer 1 is going to go for 100 tokens
        buyer.approve_and_stake(round_id, buyer.web3.to_wei(100, 'ether'))

        # close the round and try and buy some more after the round has expired
        admin.increase_evm_time(duration=60)
        try:
            buyer.approve_and_stake(round_id, buyer.web3.to_wei(100, 'ether'), expect_fail=True)
            self.addOutcome(FAILED, outcomeReason='Attempt to buy succeeded when it should fail')
        except Exception as e:
            self.log.warn('Exception raised when trying to buy more tokens')
            self.addOutcome(PASSED, outcomeReason='Attempt to buy should fail')

