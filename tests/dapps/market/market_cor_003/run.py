from ten.test.utils.properties import Properties
from ten.test.contracts.market import MarketPlace
from ten.test.dapps.market.markettest import MarketDappTest, Round


class PySysTest(MarketDappTest):

    def execute(self):
        props = Properties()
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=props.market_deployer_pk())

        # create a default round
        market = MarketPlace(self, web3)
        tx_receipt, id = self.create_default_round(market, network, web3, account, duration=60)
        target = market.contract.functions.buyProtectedTokens(id, 10)
        self.increase_evm_time(duration=60)

