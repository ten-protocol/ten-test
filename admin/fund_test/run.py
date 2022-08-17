import json, os
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.utils.keys import pk_to_account
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
        web3, deploy_account = network.connect(Properties().funded_deployment_account_pk(self.env), network.HOST, network.PORT)
        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            jam_cntr = web3.eth.contract(address=Properties().l2_jam_token_address(self.env), abi=json.load(f))

        # run for users
        for user in self.USERS:
            user_address = pk_to_account(user).address
            _, _ = network.connect(user, network.HOST, network.PORT)
            self.log.info('Running for address %s' % user_address)

            # balance before transaction
            deploy_balance = jam_cntr.functions.balanceOf(deploy_account.address).call()
            user_balance = jam_cntr.functions.balanceOf(user_address).call({'from':user_address})
            self.log.info('  L2 balances')
            self.log.info('    Deploy account balance = %d ' % deploy_balance)
            self.log.info('    User account balance = %d ' % user_balance)

            if not self.DISPLAY and user_balance < self.AMOUNT:
                amount = self.AMOUNT - user_balance

                # transfer funds from the deployment address to the user account
                self.log.info('User requests funds ... transferring %d' % amount)
                network.transact(self, web3, jam_cntr.functions.transfer(user_address, amount), deploy_account, 7200000)

                # balance after transaction
                deploy_balance = jam_cntr.functions.balanceOf(deploy_account.address).call()
                user_balance = jam_cntr.functions.balanceOf(user_address).call({'from':user_address})
                self.log.info('  L2 balances')
                self.log.info('    Deploy account balance = %d ' % deploy_balance)
                self.log.info('    User account balance = %d ' % user_balance)
