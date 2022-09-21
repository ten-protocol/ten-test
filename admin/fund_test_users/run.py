import json, os
from pysys.constants import PROJECT
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
    OBX_TARGET = 10 * EthereumTest.ONE_GIGA
    TOKEN_TARGET = 50 * EthereumTest.ONE_GIGA

    def execute(self):
        network = Obscuro
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))
        hoc_address = Properties().l2_hoc_token_address(self.env)
        poc_address = Properties().l2_poc_token_address(self.env)

        for user in self.USERS:
            web3_user, account_user = network.connect(self, user)
            self.log.info('')
            self.log.info('Running for user address %s' % account_user.address)
            self.fund_obx(network, web3_user, account_user, self.OBX_TARGET)
            self.transfer_token(network, 'HOC', hoc_address, web3_distro, account_distro, account_user.address)
            self.transfer_token(network, 'POC', poc_address, web3_distro, account_distro, account_user.address)

    def transfer_token(self, network, token_name, token_address, web3_from, account_from, address):
        self.log.info('Running for token %s' % token_name)

        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'erc20', 'erc20.json')) as f:
            token = web3_from.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account_from.address).call()
        self.log.info('Token balance before = %d ' % balance)

        # transfer tokens from the funded account to the distro account
        network.transact(self, web3_from, token.functions.transfer(address, self.TOKEN_TARGET), account_from, 7200000)

        balance = token.functions.balanceOf(account_from.address).call()
        self.log.info('Token balance after = %d ' % balance)
