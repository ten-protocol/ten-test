from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    USERS = [
        Properties().account1pk(),
        Properties().account2pk(),
        Properties().account3pk(),
        Properties().gameuserpk()
    ]
    OBX = 10 * EthereumTest.ONE_GIGA
    TOKENS = 50 * EthereumTest.ONE_GIGA

    def execute(self):
        network = Obscuro
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))
        hoc_address = Properties().l2_hoc_token_address(self.env)
        poc_address = Properties().l2_poc_token_address(self.env)

        for user in self.USERS:
            web3_user, account_user = network.connect(self, user)
            self.log.info('')
            self.log.info('Running for user address %s' % account_user.address)
            self.fund_obx(network, web3_user, account_user, self.OBX)
            self.transfer_token(network, 'HOC', hoc_address, web3_distro, account_distro, account_user.address, self.TOKENS)
            self.transfer_token(network, 'POC', poc_address, web3_distro, account_distro, account_user.address, self.TOKENS)


