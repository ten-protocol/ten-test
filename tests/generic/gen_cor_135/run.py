import secrets
from pysys.constants import PASSED, FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.expensive import ExpensiveContract


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)

        contract = ExpensiveContract(self, web3_deploy)
        contract.deploy(network, account_deploy)

        pk = secrets.token_hex(32)
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, network.ETH_ALLOC_EPHEMERAL)

        try:
            for i in range(30, 40):
                estimate = contract.contract.functions.exponentialOperation(i).estimate_gas()
                self.log.info('Exponential %d, gas estimate is %d WEI, %.9f ETH', i, estimate, web3.from_wei(estimate, 'ether'))

            for i in range(30, 40):
                estimate = contract.contract.functions.calculateFactorial(i).estimate_gas()
                self.log.info('Factorial %d, gas estimate is %d WEI, %.9f ETH', i, estimate, web3.from_wei(estimate, 'ether'))

            for i in range(350, 370, 2):
                estimate = contract.contract.functions.calculateFibonacci(i).estimate_gas()
                self.log.info('Fibonacci %d, gas estimate is %d WEI, %.9f ETH', i, estimate, web3.from_wei(estimate, 'ether'))

            self.addOutcome(PASSED)
        except Exception as e:
            self.log.warn('Exception thrown %s', e)
            self.addOutcome(FAILED)

        self.drain_native(web3, account, network)


