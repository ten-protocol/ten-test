import json, os
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    USERS = [
        # '0x686Ad719004590e98F182feA3516d443780C64a1',
        # '0x85E1Cc949Bca27912e3e951ad1F68afD1cc4aB15',
        # '0x7719A2b2BeC6a98508975C168A565FffCF9Dc266',
        # '0xD993601a218fB40147328ac8BCF086Dcc6eb3867',
        # '0x6Bd7B418C4f4e944571F8EE4D7DBD5E44279d579',
        # '0xa2aE6f0B2E8CC472c66905622ba244E58cB9813D',
        # '0x424706Da31E53a4859e560DB7ed908d6534973C0',
        # '0x61f991693aee28dbF4B7CBBB0ACf53ea92F219a3',
        # '0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
        # '0xFfB5982818055C507f606058d9073b2037937b9D'
        '0x7AFcBAC69f6339e29FCe40759FFBFb25F0CCe314'
    ]
    AMOUNT = 50000

    def execute(self):
        # connect to the L2 network
        network = Obscuro
        web3, deploy_account = network.connect(Properties().funded_deployment_account_pk(self.env), network.HOST, network.PORT)
        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc_token = web3.eth.contract(address=Properties().l2_hoc_token_address(self.env), abi=json.load(f))

        # run for users
        for user_address in self.USERS:
            self.log.info('Running for address %s' % user_address)

            # balance before transaction
            deploy_balance = hoc_token.functions.balanceOf(deploy_account.address).call()
            self.log.info('  L2 balances')
            self.log.info('    Deploy account balance = %d ' % deploy_balance)

            # transfer funds from the deployment address to the user account
            self.log.info('User requests funds ... transferring %d' % self.AMOUNT)
            network.transact(self, web3, hoc_token.functions.transfer(user_address, self.AMOUNT), deploy_account, 7200000)

            # balance after transaction
            deploy_balance = hoc_token.functions.balanceOf(deploy_account.address).call()
            self.log.info('  L2 balances')
            self.log.info('    Deploy account balance = %d ' % deploy_balance)
