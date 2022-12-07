from pysys.constants import FAILED, PASSED
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.gas.gas_consumer import GasConsumerBalance
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):
    REFERENCE = [21230]  # recorded on ganache

    def execute(self):
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        contract = GasConsumerBalance(self, web3)
        contract.deploy(network, account)

        est_1 = contract.contract.functions.get_balance().estimate_gas()
        self.log.info("Estimate get_balance:    %d" % est_1)

        self.percentile_difference('get_balance', self.REFERENCE[0], est_1, 5)

        tx1 = network.transact(self, web3, contract.contract.functions.get_balance(), account, contract.GAS)
        self.log.info("Gas used get_balance:    %d" % int(tx1["gasUsed"]))

        self.assertTrue(est_1 == int(tx1["gasUsed"]))

    def percentile_difference(self, text, result, reference, tolerance):
        percentile = abs(((reference - result) / reference) * 100)
        if percentile >= tolerance:
            self.log.error('Percentile difference for %s is %d (%d compared to %d)' % (text, percentile, result, reference))
            self.addOutcome(FAILED)
        else:
            self.addOutcome(PASSED)
