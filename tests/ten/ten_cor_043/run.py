from pysys.constants import FAILED, PASSED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.gas import GasConsumerMultiply


class PySysTest(GenericNetworkTest):
    REFERENCE = [21208, 21274, 21274]  # recorded on ganache

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        contract = GasConsumerMultiply(self, web3)
        contract.deploy(network, account)

        est_1 = contract.contract.functions.times_once().estimate_gas()
        est_2 = contract.contract.functions.times_twice().estimate_gas()
        est_3 = contract.contract.functions.times_thrice().estimate_gas()
        self.log.info("  Estimate times_once:           %d", est_1)
        self.log.info("  Estimate times_twice:          %d", est_2)
        self.log.info("  Estimate times_thrice:         %d", est_3)

        # validate 40% difference tolerance from reference
        self.percentile_difference('times_once',self.REFERENCE[0],est_1,'reference','estimate',40)
        self.percentile_difference('times_twice',self.REFERENCE[1],est_2,'reference','estimate',40)
        self.percentile_difference('times_thrice',self.REFERENCE[2],est_3,'reference','estimate',40)

        tx1 = network.transact(self, web3, contract.contract.functions.times_once(), account, contract.GAS_LIMIT)
        tx2 = network.transact(self, web3, contract.contract.functions.times_twice(), account, contract.GAS_LIMIT)
        tx3 = network.transact(self, web3, contract.contract.functions.times_thrice(), account, contract.GAS_LIMIT)
        self.log.info("  Gas used times_once:           %d", int(tx1["gasUsed"]))
        self.log.info("  Gas used times_twice:          %d", int(tx2["gasUsed"]))
        self.log.info("  Gas used times_thrice:         %d", int(tx3["gasUsed"]))

        # validate 5% difference tolerance from estimates
        self.percentile_difference('times_once',self.REFERENCE[0],int(tx1["gasUsed"]),'reference','gasUsed',5)
        self.percentile_difference('times_twice',self.REFERENCE[1],int(tx2["gasUsed"]),'reference','gasUsed',5)
        self.percentile_difference('times_thrice',self.REFERENCE[2],int(tx3["gasUsed"]),'reference','gasUsed',5)

    def percentile_difference(self, text, num1, num2, num1_txt, num2_txt, tolerance):
        percentile = abs(((num1 - num2) / num1) * 100)
        if percentile >= tolerance:
            self.log.error('  Percentile difference for %s is %d (%s %d, %s %d)',text,percentile,num1_txt,num1,num2_txt,num2)
            self.addOutcome(FAILED)
        else:
            self.log.info('  Percentile difference for %s is %d (%s %d, %s %d)',text,percentile,num1_txt,num1,num2_txt,num2)
            self.addOutcome(PASSED)
