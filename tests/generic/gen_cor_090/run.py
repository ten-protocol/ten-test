from pysys.constants import FAILED, PASSED
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.gas import GasConsumerAdd
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):
    REFERENCE = [21209, 21274, 21231, 21208]  # recorded on ganache

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        contract = GasConsumerAdd(self, web3)
        contract.deploy(network, account)

        est_1 = contract.contract.functions.add_once().estimate_gas()
        est_2 = contract.contract.functions.add_twice().estimate_gas()
        est_3 = contract.contract.functions.add_thrice().estimate_gas()
        est_4 = contract.contract.functions.add_three_times_with_a_long_name().estimate_gas()
        self.log.info("Estimate add_once:                          %d" % est_1)
        self.log.info("Estimate add_twice:                         %d" % est_2)
        self.log.info("Estimate add_thrice:                        %d" % est_3)
        self.log.info("Estimate add_three_times_with_a_long_name:  %d" % est_4)

        # validate 5% difference tolerance from reference
        self.percentile_difference('add_once', self.REFERENCE[0], est_1, 5)
        self.percentile_difference('add_twice', self.REFERENCE[1], est_2, 5)
        self.percentile_difference('add_thrice', self.REFERENCE[2], est_3, 5)
        self.percentile_difference('add_three_times_with_a_long_name', self.REFERENCE[3], est_4, 5)

        tx1 = network.transact(self, web3, contract.contract.functions.add_once(), account, contract.GAS_LIMIT)
        tx2 = network.transact(self, web3, contract.contract.functions.add_twice(), account, contract.GAS_LIMIT)
        tx3 = network.transact(self, web3, contract.contract.functions.add_thrice(), account, contract.GAS_LIMIT)
        tx4 = network.transact(self, web3, contract.contract.functions.add_three_times_with_a_long_name(), account, contract.GAS_LIMIT)
        self.log.info("Gas used add_once:                          %d" % int(tx1["gasUsed"]))
        self.log.info("Gas used add_twice:                         %d" % int(tx2["gasUsed"]))
        self.log.info("Gas used add_thrice:                        %d" % int(tx3["gasUsed"]))
        self.log.info("Gas used add_three_times_with_a_long_name:  %d" % int(tx4["gasUsed"]))

        # validate estimate is same as actual
        self.assertTrue(est_1 == int(tx1["gasUsed"]))
        self.assertTrue(est_2 == int(tx2["gasUsed"]))
        self.assertTrue(est_3 == int(tx3["gasUsed"]))
        self.assertTrue(est_4 == int(tx4["gasUsed"]))

    def percentile_difference(self, text, result, reference, tolerance):
        percentile = abs(((reference - result) / reference) * 100)
        if percentile >= tolerance:
            self.log.error('Percentile difference for %s is %d (%d compared to %d)' % (text, percentile, result, reference))
            self.addOutcome(FAILED)
        else:
            self.addOutcome(PASSED)
