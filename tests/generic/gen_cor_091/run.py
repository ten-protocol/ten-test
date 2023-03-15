from pysys.constants import FAILED, PASSED
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.gas import GasConsumerMultiply
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):
    REFERENCE = [21208, 21274, 21274]  # recorded on ganache

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        contract = GasConsumerMultiply(self, web3)
        contract.deploy(network, account)

        est_1 = contract.contract.functions.times_once().estimate_gas()
        est_2 = contract.contract.functions.times_twice().estimate_gas()
        est_3 = contract.contract.functions.times_thrice().estimate_gas()
        self.log.info("Estimate times_once:           %d" % est_1)
        self.log.info("Estimate times_twice:          %d" % est_2)
        self.log.info("Estimate times_thrice:         %d" % est_3)

        # validate 5% difference tolerance from reference
        self.percentile_difference('times_once', self.REFERENCE[0], est_1, 5)
        self.percentile_difference('times_twice', self.REFERENCE[1], est_2, 5)
        self.percentile_difference('times_thrice', self.REFERENCE[2], est_3, 5)

        tx1 = network.transact(self, web3, contract.contract.functions.times_once(), account, contract.GAS_LIMIT)
        tx2 = network.transact(self, web3, contract.contract.functions.times_twice(), account, contract.GAS_LIMIT)
        tx3 = network.transact(self, web3, contract.contract.functions.times_thrice(), account, contract.GAS_LIMIT)
        self.log.info("Gas used times_once:           %d" % int(tx1["gasUsed"]))
        self.log.info("Gas used times_twice:          %d" % int(tx2["gasUsed"]))
        self.log.info("Gas used times_thrice:         %d" % int(tx3["gasUsed"]))

        self.assertTrue(est_1 == int(tx1["gasUsed"]))
        self.assertTrue(est_2 == int(tx2["gasUsed"]))
        self.assertTrue(est_3 == int(tx3["gasUsed"]))

    def percentile_difference(self, text, result, reference, tolerance):
        percentile = abs(((reference - result) / reference) * 100)
        if percentile >= tolerance:
            self.log.error('Percentile difference for %s is %d (%d compared to %d)' % (text, percentile, result, reference))
            self.addOutcome(FAILED)
        else:
            self.addOutcome(PASSED)
