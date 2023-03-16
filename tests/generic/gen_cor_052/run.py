from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.contracts.payable import ReceiveEther, SendEther


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # deploy the contracts
        rcv_eth = ReceiveEther(self, web3)
        rcv_eth.deploy(network, account)

        snd_eth = SendEther(self, web3)
        snd_eth.deploy(network, account)
