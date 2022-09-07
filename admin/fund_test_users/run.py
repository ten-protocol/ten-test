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

    def execute(self):
        network = Obscuro
        web3_deploy, deploy_account = network.connect(Properties().funded_deployment_account_pk(self.env), network.HOST,
                                                      network.PORT)
        web3_faucet, faucet_account = network.connect(Properties().faucet_pk(self.env), network.HOST,
                                                      network.ACCOUNT2_PORT)

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc = web3_deploy.eth.contract(address=Properties().l2_hoc_token_address(self.env), abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            poc = web3_deploy.eth.contract(address=Properties().l2_poc_token_address(self.env), abi=json.load(f))

        for user in self.USERS:
            web3_user, user_account = network.connect(user, network.HOST, network.PORT)
            self.log.info('')
            self.log.info('Running for user address %s' % user_account.address)
            self.fund_obx(network, web3_user, user_account, web3_faucet, faucet_account)
            self.fund_token(network, 'HOC', hoc, web3_user, user_account, web3_deploy, deploy_account, web3_faucet, faucet_account)
            self.fund_token(network, 'POC', poc, web3_user, user_account, web3_deploy, deploy_account, web3_faucet, faucet_account)


