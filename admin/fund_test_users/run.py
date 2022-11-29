from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.obscuro import Obscuro


class PySysTest(ObscuroNetworkTest):
    USERS = [
        Properties().account1pk(),
        Properties().account2pk(),
        Properties().account3pk(),
        Properties().account4pk()
    ]
    OBX = Web3().toWei(100, 'ether')
    TOKENS = Web3().toWei(50, 'ether')

    def execute(self):
        network = Obscuro
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))
        hoc_address = Properties().l2_hoc_token_address(self.env)
        poc_address = Properties().l2_poc_token_address(self.env)

        for user in self.USERS:
            web3_user, account_user = network.connect(self, user)
            self.log.info('')
            self.log.info('Running for user address %s' % account_user.address)
            self.log.info('Funding native OBX to the test user account')
            self.fund_obx(network, account_user, self.OBX, web3_user)

            if not self.is_obscuro_sim():
                self.log.info('Funding HOC and POC to the test user account')
                self.transfer_token(network, 'HOC', hoc_address, web3_distro, account_distro, account_user.address, self.TOKENS)
                self.transfer_token(network, 'POC', poc_address, web3_distro, account_distro, account_user.address, self.TOKENS)


