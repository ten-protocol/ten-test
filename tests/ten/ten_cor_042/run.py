from pysys.constants import FAILED, PASSED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.gas import GasConsumerAdd


class PySysTest(GenericNetworkTest):
    REFERENCE = [21209, 21274, 21231, 21208]  # recorded on ganache

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        contract = GasConsumerAdd(self, web3)
        contract.deploy(network, account)

        est_1 = contract.contract.functions.add_once().estimate_gas()
        est_2 = contract.contract.functions.add_twice().estimate_gas()
        est_3 = contract.contract.functions.add_thrice().estimate_gas()
        est_4 = contract.contract.functions.add_three_times_with_a_long_name().estimate_gas()
        self.log.info("  Estimate add_once:                          %d", est_1)
        self.log.info("  Estimate add_twice:                         %d", est_2)
        self.log.info("  Estimate add_thrice:                        %d", est_3)
        self.log.info("  Estimate add_three_times_with_a_long_name:  %d", est_4)

        # validate 40% difference tolerance in the estimate from the reference
        self.percentile_difference('add_once',self.REFERENCE[0],est_1,'reference','estimate',51)
        self.percentile_difference('add_twice',self.REFERENCE[1],est_2,'reference','estimate',51)
        self.percentile_difference('add_thrice',self.REFERENCE[2],est_3,'reference','estimate',51)
        self.percentile_difference('add_three_times_with_a_long_name',self.REFERENCE[3],est_4,'reference','estimate',51)

        tx1 = network.transact(self, web3, contract.contract.functions.add_once(), account, contract.GAS_LIMIT)
        tx2 = network.transact(self, web3, contract.contract.functions.add_twice(), account, contract.GAS_LIMIT)
        tx3 = network.transact(self, web3, contract.contract.functions.add_thrice(), account, contract.GAS_LIMIT)
        tx4 = network.transact(self, web3, contract.contract.functions.add_three_times_with_a_long_name(), account, contract.GAS_LIMIT)
        self.log.info("  Gas used add_once:                          %d", int(tx1["gasUsed"]))
        self.log.info("  Gas used add_twice:                         %d", int(tx2["gasUsed"]))
        self.log.info("  Gas used add_thrice:                        %d", int(tx3["gasUsed"]))
        self.log.info("  Gas used add_three_times_with_a_long_name:  %d", int(tx4["gasUsed"]))

        # validate 5% difference tolerance from estimate
        self.percentile_difference('add_once',self.REFERENCE[0],int(tx1["gasUsed"]),'reference','gasUsed',5)
        self.percentile_difference('add_twice',self.REFERENCE[1],int(tx2["gasUsed"]),'reference','gasUsed',5)
        self.percentile_difference('add_thrice',self.REFERENCE[2],int(tx3["gasUsed"]),'reference','gasUsed',5)
        self.percentile_difference('add_three_times_with_a_long_name',self.REFERENCE[3],int(tx4["gasUsed"]),'reference','gasUsed',5)

    def percentile_difference(self, text, num1, num2, num1_txt, num2_txt, tolerance):
        percentile = abs(((num1 - num2) / num1) * 100)
        if percentile >= tolerance:
            self.log.error('  Percentile difference for %s is %d (%s %d, %s %d)',text,percentile,num1_txt,num1,num2_txt,num2)
            self.addOutcome(FAILED)
        else:
            self.log.info('  Percentile difference for %s is %d (%s %d, %s %d)',text,percentile,num1_txt,num1,num2_txt,num2)
            self.addOutcome(PASSED)
