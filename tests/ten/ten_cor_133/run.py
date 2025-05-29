import time
from web3._utils.events import EventLogErrorFlags
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.system import TenSystemCallsCaller


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()

        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        caller = TenSystemCallsCaller(self, web3)
        caller.deploy(network, account)

        # send in the transactions
        latencies = []
        for i in range(0,99): latencies.append(self.transact(1, network, web3, account, caller, props))
        avg_latency = (sum(latencies) / len(latencies))
        self.log.info('Average latency is %d' % avg_latency)
        self.assertTrue(avg_latency < 500, assertMessage='Average latency should be less than 500ms')

    def transact(self, id, network, web3, account, caller, props):
        current_time = time.time_ns() // 1_000_000
        target = caller.contract.functions.emitTimestamp(id, props.L2TenSystemCalls)
        receipt = network.transact(self, web3, target, account, caller.GAS_LIMIT)
        logs = caller.contract.events.TxTimestamp().process_receipt(receipt, EventLogErrorFlags.Discard)
        timestamp = logs[0]['args']['timestamp']
        return (timestamp - current_time)

