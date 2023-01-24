from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):
    USERS = [
        Properties().account1_1pk(), Properties().account2_1pk(), Properties().account3_1pk(), Properties().account4_1pk(),
        Properties().account1_2pk(), Properties().account2_2pk(), Properties().account3_2pk(), Properties().account4_2pk(),
        Properties().account1_3pk(), Properties().account2_3pk(), Properties().account3_3pk(), Properties().account4_3pk()
    ]
    OBX = Web3().toWei(100, 'ether')

    def execute(self):
        network = NetworkFactory.get_network(self)

        for user in self.USERS:
            web3_user, account_user = network.connect(self, user)
            self.log.info('')
            self.log.info('Running for user address %s' % account_user.address)
            self.fund_obx(network, account_user, self.OBX, web3_user)
