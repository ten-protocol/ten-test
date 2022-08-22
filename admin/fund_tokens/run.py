import json, os, time
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.factory import NetworkFactory
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):
    AMOUNT = 10000000000000
    THRESHOLD = 1000000000000

    def execute(self):
        # connect to the L1 network and get contracts
        l1 = NetworkFactory.get_l1_network(self.env)
        bridge_address = Properties().management_bridge_address(self.env)
        deployment_pk = Properties().funded_deployment_account_pk(self.env)
        web3_l1, deploy_account_l1 = l1.connect(deployment_pk, l1.HOST, l1.PORT)

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc_token_l1 = web3_l1.eth.contract(address=Properties().l1_hoc_token_address(self.env), abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            poc_token_l1 = web3_l1.eth.contract(address=Properties().l1_poc_token_address(self.env), abi=json.load(f))

        # connect to the L2 network and get contracts
        l2 = Obscuro
        deployment_pk = Properties().funded_deployment_account_pk(self.env)
        web3_l2, _ = l2.connect(deployment_pk, l2.HOST, l2.PORT)

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc_token_l2 = web3_l2.eth.contract(address=Properties().l2_hoc_token_address(self.env), abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            poc_token_l2 = web3_l2.eth.contract(address=Properties().l2_poc_token_address(self.env), abi=json.load(f))

        self.run_for_token('HOC', l1, hoc_token_l1, hoc_token_l2, bridge_address, deploy_account_l1, web3_l1)
        self.run_for_token('POC', l1, poc_token_l1, poc_token_l2, bridge_address, deploy_account_l1, web3_l1)

    def run_for_token(self, token_name, layer1, token_l1, token_l2,
                      bridge_address, deploy_account,
                      web3_l1):
        self.log.info('Running for token %s' % token_name)

        deploy_balance_l2_before = token_l2.functions.balanceOf(deploy_account.address).call()
        self.log.info('L2 balance before;')
        self.log.info('  Deploy balance = %d ' % deploy_balance_l2_before)

        if deploy_balance_l2_before < self.THRESHOLD:
            amount = (self.AMOUNT - deploy_balance_l2_before)
            self.log.info('Deployment account balance is %d ... transferring %d ' % (self.THRESHOLD, amount))

            # transfer funds from the deployment address to the bridge address on l1
            layer1.transact(self, web3_l1, token_l1.functions.transfer(bridge_address, amount), deploy_account, 7200000)

            time.sleep(30)
            deploy_balance_l2_after = token_l2.functions.balanceOf(deploy_account.address).call()
            self.log.info('L2 Balances after;')
            self.log.info('  Deploy Account balance = %d ' % deploy_balance_l2_after)

            self.assertTrue((deploy_balance_l2_after - deploy_balance_l2_before) == amount)



