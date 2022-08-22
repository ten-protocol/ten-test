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

    AMOUNT = 5000
    DISPLAY = False

    def execute(self):
        # connect to the L2 network
        network = Obscuro

        web3_deploy, deploy_account = network.connect(Properties().funded_deployment_account_pk(self.env), network.HOST, network.PORT)
        web3_faucet, faucet_account = network.connect(Properties().faucet_pk(self.env), network.HOST, network.ACCOUNT2_PORT)
        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc_token = web3_deploy.eth.contract(address=Properties().l2_hoc_token_address(self.env), abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            poc_token = web3_deploy.eth.contract(address=Properties().l2_poc_token_address(self.env), abi=json.load(f))

        self.run_for_token(network, 'HOC', hoc_token, web3_deploy, deploy_account, web3_faucet, faucet_account)
        self.run_for_token(network, 'POC', poc_token, web3_deploy, deploy_account, web3_faucet, faucet_account)


    def run_for_token(self, network, token_name, token,
                      web3_deploy, deploy_account,
                      web3_faucet, faucet_account):

        # run for users
        for user in self.USERS:
            self.log.info('')
            self.log.info('Running for token %s' % token_name)
            web3_user, user_account = network.connect(user, network.HOST, network.PORT)
            self.log.info('Running for address %s' % user_account.address)

            # balance before transaction
            deploy_balance = token.functions.balanceOf(deploy_account.address).call()
            user_balance = token.functions.balanceOf(user_account.address).call({'from': user_account.address})
            faucet_obx_balance = web3_faucet.eth.get_balance(faucet_account.address)
            deploy_obx_balance = web3_deploy.eth.get_balance(deploy_account.address)
            user_obx_balance = web3_user.eth.get_balance(user_account.address)
            self.log.info('  L2 balances before;')
            self.log.info('    OBX Faucet balance = %d ' % faucet_obx_balance)
            self.log.info('    OBX Deploy account balance = %d ' % deploy_obx_balance)
            self.log.info('    OBX User balance = %d ' % user_obx_balance)
            self.log.info('    %s Deploy account balance = %d ' % (token_name, deploy_balance))
            self.log.info('    %s User account balance = %d ' % (token_name, user_balance))

            if not self.DISPLAY and user_balance < self.AMOUNT:
                amount = self.AMOUNT - user_balance

                # transfer funds from the deployment address to the user account
                self.log.info('User requests funds ... transferring %d' % amount)
                network.transact(self, web3_deploy, token.functions.transfer(user_account.address, amount),
                                 deploy_account, 7200000)

                # balance after transaction
                deploy_balance = token.functions.balanceOf(deploy_account.address).call()
                user_balance = token.functions.balanceOf(user_account.address).call({'from': user_account.address})
                faucet_obx_balance = web3_faucet.eth.get_balance(faucet_account.address)
                deploy_obx_balance = web3_deploy.eth.get_balance(deploy_account.address)
                user_obx_balance = web3_user.eth.get_balance(user_account.address)
                self.log.info('  L2 balances after;')
                self.log.info('    OBX Faucet balance = %d ' % faucet_obx_balance)
                self.log.info('    OBX Deploy account balance = %d ' % deploy_obx_balance)
                self.log.info('    OBX User balance = %d ' % user_obx_balance)
                self.log.info('    %s Deploy account balance = %d ' % (token_name, deploy_balance))
                self.log.info('    %s User account balance = %d ' % (token_name, user_balance))

            self.log.info('')