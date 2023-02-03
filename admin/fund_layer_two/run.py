from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):
    DIST_OBX = 5000
    USER_OBX = 100

    USERS = [
        Properties().account1_1pk(), Properties().account2_1pk(), Properties().account3_1pk(), Properties().account4_1pk(),
        Properties().account1_2pk(), Properties().account2_2pk(), Properties().account3_2pk(), Properties().account4_2pk(),
        Properties().account1_3pk(), Properties().account2_3pk(), Properties().account3_3pk(), Properties().account4_3pk()
    ]

    def execute(self):
        # connect to the L2 network
        network = NetworkFactory.get_network(self)
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))

        # log the current balance
        balance = web3_distro.eth.get_balance(account_distro.address)
        self.log.info("Current balance for the distro account = %d " % balance)

        # fund obx to the distro account on l2
        self.log.info('')
        self.log.info('Funding native OBX to the distro account')
        self.fund_obx(network, account_distro, self.DIST_OBX, web3_distro)

        for user in self.USERS:
            web3_user, account_user = network.connect(self, user)
            self.log.info('')
            self.log.info('Funding native OBX to the users account %s' % account_user.address)
            self.fund_obx(network, account_user, self.USER_OBX, web3_user)

