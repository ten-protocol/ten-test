from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.obscuro import Obscuro


class PySysTest(ObscuroNetworkTest):
    OBX = Web3().toWei(50000, 'ether')

    def execute(self):
        # connect to the L2 network
        network = Obscuro
        hoc_address = Properties().l2_hoc_token_address(self.env)
        poc_address = Properties().l2_poc_token_address(self.env)
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))

        # log the current balance
        balance = web3_distro.eth.get_balance(account_distro.address)
        self.log.info("Current balance for the distro account = %d " % balance)

        # fund obx to the distro account on l2
        self.log.info('')
        self.log.info('Funding native OBX to the distro account')
        self.fund_obx(network, web3_distro, account_distro, self.OBX)

        if not self.is_obscuro_sim():
            # print the ERC20 balances as a check
            self.log.info('')
            self.log.info('Printing HOC and POC balances for the distro account')
            self.print_token_balance('HOC', hoc_address, web3_distro, account_distro)
            self.print_token_balance('HOC', poc_address, web3_distro, account_distro)

