import secrets, time
from collections import deque
from pysys.constants import PASSED, FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.expensive import ExpensiveContract


class RollingSum:
    def __init__(self, interval=60):
        self.interval = interval
        self.data = deque()
        self.current_sum = 0.0

    def add_value(self, value):
        current_time = time.time()
        self.data.append((current_time, value))
        self.current_sum += value
        self._remove_old_entries(current_time)

    def get_sum(self):
        current_time = time.time()
        self._remove_old_entries(current_time)
        return self.current_sum

    def _remove_old_entries(self, current_time):
        while self.data and current_time - self.data[0][0] > self.interval:
            _, old_value = self.data.popleft()
            self.current_sum -= old_value

class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3_deploy, account_deploy = network.connect_account1(self)

        contract = ExpensiveContract(self, web3_deploy)
        contract.deploy(network, account_deploy)

        pk = secrets.token_hex(32)
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, network.ETH_ALLOC_EPHEMERAL)

        rolling_sum = RollingSum()
        try:
            for i in range(30, 40):
                start_time = time.perf_counter()
                estimate = contract.contract.functions.exponentialOperation(i).estimate_gas()
                end_time = time.perf_counter()
                self.log.info('Exponential %d, gas estimate %d WEI, %.9f ETH, duration %.9f',
                              i, estimate, web3.from_wei(estimate, 'ether'), end_time-start_time)
                rolling_sum.add_value(end_time-start_time)
                self.log.info('Rolling sum is %.9f' % rolling_sum.current_sum)

            for i in range(30, 40):
                start_time = time.perf_counter()
                estimate = contract.contract.functions.calculateFactorial(i).estimate_gas()
                end_time = time.perf_counter()
                self.log.info('Factorial %d, gas estimate is %d WEI, %.9f ETH, duration %.9f',
                              i, estimate, web3.from_wei(estimate, 'ether'), end_time-start_time)
                rolling_sum.add_value(end_time-start_time)
                self.log.info('Rolling sum is %.9f' % rolling_sum.current_sum)

            for i in range(350, 370, 2):
                start_time = time.perf_counter()
                estimate = contract.contract.functions.calculateFibonacci(i).estimate_gas()
                end_time = time.perf_counter()
                self.log.info('Fibonacci %d, gas estimate is %d WEI, %.9f ETH, duration %.9f',
                              i, estimate, web3.from_wei(estimate, 'ether'), end_time-start_time)
                rolling_sum.add_value(end_time-start_time)

                while  ( (rolling_sum.current_sum + (end_time-start_time) ) > 10.0):
                    rolling_sum._remove_old_entries(time.time())
                    time.sleep(1)

                self.log.info('Rolling sum is %.9f' % rolling_sum.current_sum)
            self.addOutcome(PASSED)

        except Exception as e:
            self.log.warn('Exception thrown %s', e)
            self.addOutcome(FAILED)

        self.drain_native(web3, account, network)


