from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):
    ETH = Web3().toWei(10, 'ether')

    def execute(self):
        # connect to the L1 network
        network = NetworkFactory.get_l1_network(self)
        web3_funded_l1, account_funded_l1 = network.connect(self, Properties().l1_funded_account_pk(self.env))
        web3_distro_l1, account_distro_l1 = network.connect(self, Properties().distro_account_pk(self.env))

        # fund eth to the distro account
        self.log.info('')
        self.log.info('Funding native ETH to the distro account')
        self.fund_eth(network, web3_funded_l1, account_funded_l1, web3_distro_l1, account_distro_l1, 10)

