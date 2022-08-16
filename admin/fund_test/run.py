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
        l2 = Obscuro
        web3_l2, deploy_account = l2.connect(Properties().funded_deployment_account_pk(l2.PROPS_KEY), l2.HOST, l2.PORT)
        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            jam_cntr = web3_l2.eth.contract(address=Properties().l2_jam_token_address(l2.PROPS_KEY), abi=json.load(f))

        # run for users
        for user in self.USERS:
            user_address = pk_to_account(user).address
            _, _ = l2.connect(user, l2.HOST, l2.PORT)
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
                l2.transact(self, web3_l2, jam_cntr.functions.transfer(user_address, amount), deploy_account, 7200000)

                # balance after transaction
                deploy_balance = jam_cntr.functions.balanceOf(deploy_account.address).call()
                user_balance = jam_cntr.functions.balanceOf(user_address).call({'from':user_address})
                self.log.info('  L2 balances')
                self.log.info('    Deploy account balance = %d ' % deploy_balance)
                self.log.info('    User account balance = %d ' % user_balance)
