from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    OBX = 10000 * EthereumTest.ONE_GIGA

    def execute(self):
        # connect to the L2 network
        network = Obscuro
        hoc_address = Properties().l2_hoc_token_address(self.env)
        poc_address = Properties().l2_poc_token_address(self.env)
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))

        # fund obx to the distro account on l2
        self.log.info('')
        self.log.info('Funding native OBX to the distro account')
        self.fund_obx(network, web3_distro, account_distro, self.OBX)

        # print the ERC20 balances as a check
        self.print_token_balance('HOC', hoc_address, web3_distro, account_distro)
        self.print_token_balance('HOC', poc_address, web3_distro, account_distro)

