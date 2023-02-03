from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):
    DIST_AMOUNT = 50
    USER_AMOUNT = 1

    USERS = [
        Properties().account1_1pk(), Properties().account2_1pk(), Properties().account3_1pk(), Properties().account4_1pk(),
        Properties().account1_2pk(), Properties().account2_2pk(), Properties().account3_2pk(), Properties().account4_2pk(),
        Properties().account1_3pk(), Properties().account2_3pk(), Properties().account3_3pk(), Properties().account4_3pk()
    ]

    def execute(self):
        # connect to the L1 network
        network = NetworkFactory.get_l1_network(self)
        web3_funded_l1, account_funded_l1 = network.connect(self, Properties().l1_funded_account_pk(self.env))
        web3_distro_l1, account_distro_l1 = network.connect(self, Properties().distro_account_pk(self.env))

        # fund eth to the distro account
        self.log.info('')
        self.log.info('Funding native ETH to the distro account')
        self.fund_eth(network, web3_funded_l1, account_funded_l1, web3_distro_l1, account_distro_l1, self.DIST_AMOUNT)

        for user in self.USERS:
            web3_user, account_user = network.connect(self, user)
            self.log.info('')
            self.log.info('Funding native ETH to the users account %s' % account_user.address)
            self.fund_eth(network, web3_distro_l1, account_distro_l1, web3_user, account_user, self.USER_AMOUNT)
