from time import time
from decimal import Decimal
from pysys.constants import FAILED
from ten.test.basetest import GenericNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.market import MarketPlace

def to_ray(amount):
    return int(Decimal(amount) * 10 ** 27)

class PySysTest(GenericNetworkTest):

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
        round_id = market.contract.functions.latestRoundId().call()
        self.log.info('Latest round id is %d' % round_id)

        # create a new round
        self.create_round(market, network, web3, account,
                          deadline=int(time()) + 60,
                          price=web3.to_wei(1, 'ether'),
                          beta=to_ray(0.25),
                          tenCap = web3.to_wei(1000, 'ether'),
                          maxUSDC = 0,
                          minUSDC = 500 * web3.to_wei(1, 'ether'))

        # get the latest round id
        round_id = market.contract.functions.latestRoundId().call()
        self.log.info('Latest round id is %d' % round_id)

    def create_round(self, market, network, web3, account, deadline, price, beta, tenCap, maxUSDC, minUSDC):
        target = market.contract.functions.createRound(deadline, price, beta, tenCap, maxUSDC, minUSDC)
        tx_receipt = network.transact(self, web3, target, account, market.GAS_LIMIT, persist_nonce=False)
        return tx_receipt