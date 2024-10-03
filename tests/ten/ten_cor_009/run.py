from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import Relevancy
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy a contract and get the debug event log relevancy on the TwoIndexedAddresses event
        relevancy = Relevancy(self, web3)
        relevancy.deploy(network, account)
        self.log.info('Relevancy contract address is %s', relevancy.address)
        response = self.get_debug_event_log_relevancy(relevancy.address, '0x85217d12aec82988299a2d33c06c6d141fb9af7717cb74856740aad1f0a3b8e9')
        self.log.info(response)
