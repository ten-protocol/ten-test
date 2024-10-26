from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import Relevancy


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy a contract and get the debug event log relevancy on the TwoIndexedAddresses event
        relevancy = Relevancy(self, web3)
        relevancy.deploy(network, account)
        self.log.info('Relevancy contract address is %s', relevancy.address)

        response = self.get_debug_event_log_relevancy(
            url=network.connection_url(),
            address=relevancy.address,
            signature=web3.keccak(text='TwoIndexedAddresses(address,address)').hex())
        self.log.info('Returned response: %s', response)
