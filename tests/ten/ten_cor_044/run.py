from pysys.constants import FAILED, PASSED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.gas import GasConsumerBalance


class PySysTest(GenericNetworkTest):
    REFERENCE = [21230]  # recorded on ganache

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        contract = GasConsumerBalance(self, web3)
        contract.deploy(network, account)

        est_1 = contract.contract.functions.get_balance().estimate_gas()
        self.log.info("  Estimate get_balance:    %d", est_1)
        self.percentile_difference('get_balance',self.REFERENCE[0],est_1,'reference','estimate',50)

        tx1 = network.transact(self, web3, contract.contract.functions.get_balance(), account, contract.GAS_LIMIT)
        self.log.info("  Gas used get_balance:    %d", int(tx1["gasUsed"]))
        self.percentile_difference('get_balance',self.REFERENCE[0],int(tx1["gasUsed"]),'reference','gasUsed',5)

    def percentile_difference(self, text, num1, num2, num1_txt, num2_txt, tolerance):
        percentile = abs(((num1 - num2) / num1) * 100)
        if percentile >= tolerance:
            self.log.error('  Percentile difference for %s is %d (%s %d, %s %d)',text,percentile,num1_txt,num1,num2_txt,num2)
            self.addOutcome(FAILED)
        else:
            self.log.info('  Percentile difference for %s is %d (%s %d, %s %d)',text,percentile,num1_txt,num1,num2_txt,num2)
            self.addOutcome(PASSED)
