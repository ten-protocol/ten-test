from pysys.constants import FAILED, PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        network = self.get_l1_network_connection()
        web3, account = network.connect_account1(self)

        self.check_has_code('L1BridgeAddress', props.L1BridgeAddress, web3)
        self.check_has_code('L1MessageBusAddress', props.L1MessageBusAddress, web3)
        self.check_has_code('L1ManagementAddress', props.L1CrossChainManagementAddress, web3)
        self.check_has_code('L1CrossChainMessengerAddress', props.L1CrossChainMessengerAddress, web3)

        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        self.check_has_code('L2BridgeAddress', props.L2BridgeAddress, web3)
        self.check_has_code('L2MessageBusAddress', props.L2MessageBusAddress, web3)
        self.check_has_code('L2CrossChainMessengerAddress', props.L2CrossChainMessengerAddress, web3)

    def check_has_code(self, name, address, web3):
        if web3.eth.get_code(address) == b'':
            self.log.error('  Deployed contract %s at %s has no code' % (name, address))
            self.addOutcome(FAILED, abortOnError=False)
        else:
            self.log.info('  Deployed contract %s at %s has code' % (name, address))
            self.addOutcome(PASSED)