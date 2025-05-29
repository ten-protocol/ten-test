from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.system import TenSystemCallsCaller


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()

        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        caller = TenSystemCallsCaller(self, web3)
        caller.deploy(network, account)

        id = 1
        target = caller.contract.functions.emitRandomNumber(id, props.L2TenSystemCalls).call()
        network.transact(self, web3, target, account, caller.GAS_LIMIT)


