from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy a contract and get the debug event log relevancy on the Storage event
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        self.log.info('Storage contract address is %s', storage.address)
        response = self.get_debug_event_log_relevancy(storage.address, '0xc6d8c0af6d21f291e7c359603aa97e0ed500f04db6e983b9fce75a91c6b8da6b')
        self.log.info(response)

