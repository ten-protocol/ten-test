import secrets, os
from pysys.constants import PROJECT
from obscuro.test.basetest import ObscuroTest
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroTest):

    def execute(self):
        network = NetworkFactory.get_l1_network(self.env)
        hoc_address_l1 = Properties().l1_hoc_token_address(self.env)
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))

        private_key = secrets.token_hex(32)
        web3_user, account_user = network.connect(self, private_key)
        self.fund_eth(network, web3_distro, account_distro, web3_user, account_user, 0.01)

        self.print_token_balance('HOC', hoc_address_l1, web3_distro, account_distro)
        self.transfer_token(network, 'HOC', hoc_address_l1, web3_distro, account_distro, account_user.address, 1)
        self.print_token_balance('HOC', hoc_address_l1, web3_user, account_user)