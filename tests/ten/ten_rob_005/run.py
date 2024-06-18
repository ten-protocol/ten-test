from ten.test.basetest import TenNetworkTest
from ten.test.contracts.emitter import EventEmitter


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network on the primary gateway  and deploy contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        emitter = EventEmitter(self, web3, 100)
        emitter.deploy(network, account)
