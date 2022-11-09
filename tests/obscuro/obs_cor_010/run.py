import secrets
from obscuro.test.basetest import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroTest):

    def execute(self):
        network = Obscuro
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))
        hoc_address_l1 = Properties().l1_hoc_token_address(self.env)
        hoc_address_l2 = Properties().l2_hoc_token_address(self.env)

        private_key = secrets.token_hex(32)
        web3_user, account_user = network.connect(self, private_key)
        self.fund_eth(network, web3_distro, account_distro, web3_user, account_user, 0.1)


