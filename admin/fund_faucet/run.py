import json, os, time
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.factory import NetworkFactory
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    AMOUNT = 1000000
    THRESHOLD = 1000

    def execute(self):
        # connect to the L1 network
        l1 = NetworkFactory.get_l1_network(self.env)
        bridge_address = Properties().management_bridge_address(self.env)
        deployment_pk = Properties().funded_deployment_account_pk(self.env)
        web3_l1, deploy_account_l1 = l1.connect(deployment_pk, l1.HOST, l1.PORT)
        self.log.info('L1 connection details')
        self.log.info('  Bridge address = %s' % bridge_address)
        self.log.info('  Deployment PK  = %s' % deployment_pk)
        self.log.info('  Deployment ETH  = %d' % l1.get_balance(web3_l1, deploy_account_l1.address))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            jam_cntr_l1 = web3_l1.eth.contract(address=Properties().l1_hoc_token_address(self.env), abi=json.load(f))

        deploy_balance_l1 = jam_cntr_l1.functions.balanceOf(deploy_account_l1.address).call()
        self.log.info('L1 balances')
        self.log.info('  Deploy balance = %d ' % deploy_balance_l1)

        # connect to the L2 network
        l2 = Obscuro
        deployment_pk = Properties().funded_deployment_account_pk(self.env)
        web3_l2, deploy_account = l2.connect(deployment_pk, l2.HOST, l2.PORT)
        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            jam_cntr_l2 = web3_l2.eth.contract(address=Properties().l2_hoc_token_address(self.env), abi=json.load(f))

        deploy_balance_l2 = jam_cntr_l2.functions.balanceOf(deploy_account.address).call()
        self.log.info('L2 balances')
        self.log.info('  Deploy balance = %d ' % deploy_balance_l2)

        if deploy_balance_l2 < self.THRESHOLD:
            amount = (self.AMOUNT - deploy_balance_l2)
            self.log.info('Deployment account balance is < %d > - transferring %d ' % (self.THRESHOLD, amount))

            # transfer funds from the deployment address to the bridge address on l1
            l1.transact(self, web3_l1, jam_cntr_l1.functions.transfer(bridge_address, amount), deploy_account, 7200000)

            deploy_balance_l1_after = jam_cntr_l1.functions.balanceOf(deploy_account.address).call()
            self.log.info('L1 Balances after transfer')
            self.log.info('  Deploy Account balance = %d ' % deploy_balance_l1_after)

            time.sleep(30)
            deploy_balance_l2_after = jam_cntr_l2.functions.balanceOf(deploy_account.address).call()
            self.log.info('L2 Balances after transfer')
            self.log.info('  Deploy Account balance = %d ' % deploy_balance_l2_after)

            self.assertTrue((deploy_balance_l2_after - deploy_balance_l2) == amount)



