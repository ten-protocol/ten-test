import json, os
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    OBX_TARGET = 10000 * EthereumTest.ONE_GIGA

    def execute(self):
        # connect to the L2 network
        network = Obscuro
        hoc_address = Properties().l2_hoc_token_address(self.env)
        poc_address = Properties().l2_poc_token_address(self.env)
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))

        # fund obx to the distro account on l2
        self.fund_obx(network, web3_distro, account_distro, self.OBX_TARGET)

        # print the ERC20 balances as a check
        self.print_token_balance('HOC', hoc_address, web3_distro, account_distro)
        self.print_token_balance('HOC', poc_address, web3_distro, account_distro)

    def print_token_balance(self, token_name, token_address, web3_distro, account_distro):
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'erc20', 'erc20.json')) as f:
            token = web3_distro.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account_distro.address).call()
        self.log.info('Token balance for %s = %d '  % (token_name, balance))
