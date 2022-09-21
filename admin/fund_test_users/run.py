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
            self.fund_obx(network, web3_user, account_user, self.TOKEN_TARGET)
            self.fund_token(network, 'HOC', hoc_address, web3_user, account_user, web3_distro, account_distro)
            self.fund_token(network, 'POC', poc_address, web3_user, account_user, web3_distro, account_distro)

    def fund_token(self, network, token_name, token_address,
                   web3_user, account_user,
                   web3_distro, account_distro):
        """Allocates ERC20 tokens from a token contract to a users account within that contract."""
        self.log.info('Running for token %s' % token_name)

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            token_user = web3_user.eth.contract(address=token_address, abi=json.load(f))
            token_distro = web3_distro.eth.contract(address=token_address, abi=json.load(f))

        user_balance = token_user.functions.balanceOf(account_distro.address).call()
        distro_balance = token_distro.functions.balanceOf(account_distro.address).call()
        self.log.info('  Token balance before;')
        self.log.info('    Distro balance = %d ' % distro_balance)
        self.log.info('    User balance = %d ' % user_balance)

        if user_balance < self.TOKEN_TARGET:
            amount = self.TOKEN_TARGET - user_balance
            self.log.info('Below target so transferring %d' % amount)

            network.transact(self, web3_distro, token_distro.functions.transfer(account_user.address, amount),
                             account_distro, 7200000)

            user_balance = token_user.functions.balanceOf(account_distro.address).call()
            distro_balance = token_distro.functions.balanceOf(account_distro.address).call()
            self.log.info('  Token balance after;')
            self.log.info('    Distro balance = %d ' % distro_balance)
            self.log.info('    User balance = %d ' % user_balance)
