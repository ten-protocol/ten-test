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
            user_obx = web3_user.eth.get_balance(account_user.address)
            self.log.info('')
            self.log.info('Running for user address %s' % account_user.address)
            self.log.info('Funding native OBX to the test user account')
            self.log.info('OBX User balance before = %d ' % user_obx)
            self.fund_obx(network, account_user, self.OBX, web3_user)
            self.log.info('OBX User balance after = %d ' % user_obx)
