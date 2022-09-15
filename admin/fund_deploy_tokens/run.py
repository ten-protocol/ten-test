import json, os, time
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.factory import NetworkFactory
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):

    def execute(self):
        # connect to the L1 network and get contracts
        l1 = NetworkFactory.get_l1_network(self.env)
        bridge_address = Properties().management_bridge_address(self.env)
        deployment_pk = Properties().funded_deployment_account_pk(self.env)
        web3_l1, deploy_account_l1 = l1.connect(deployment_pk)

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc_l1 = web3_l1.eth.contract(address=Properties().l1_hoc_token_address(self.env), abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            poc_l1 = web3_l1.eth.contract(address=Properties().l1_poc_token_address(self.env), abi=json.load(f))

        # connect to the L2 network and get contracts
        l2 = Obscuro
        web3_l2, _ = l2.connect(deployment_pk)

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            hoc_l2 = web3_l2.eth.contract(address=Properties().l2_hoc_token_address(self.env), abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            poc_l2 = web3_l2.eth.contract(address=Properties().l2_poc_token_address(self.env), abi=json.load(f))

        # allocate the HOC and POC tokens
        self.bridge_token('HOC', l1, hoc_l1, hoc_l2, bridge_address, deploy_account_l1, web3_l1)
        self.bridge_token('POC', l1, poc_l1, poc_l2, bridge_address, deploy_account_l1, web3_l1)

    def bridge_token(self, token_name, layer1, token_l1, token_l2, bridge_address, deploy_account, web3_l1):
        self.log.info('Running for token %s' % token_name)

        balance_before = token_l2.functions.balanceOf(deploy_account.address).call()
        self.log.info('L2 token balance before;')
        self.log.info('  Balance = %d ' % balance_before)

        if balance_before < self.TOKEN_THRESHOLD:
            amount = (10000000 * self.ONE_GIGA - balance_before)
            self.log.info('Funds required, transferring %d ' % amount)

            # transfer funds from the deployment address to the bridge address on l1
            layer1.transact(self, web3_l1, token_l1.functions.transfer(bridge_address, amount), deploy_account, 7200000)

            time.sleep(30)
            balance_after = token_l2.functions.balanceOf(deploy_account.address).call()
            self.log.info('L2 token balances after;')
            self.log.info('  Balance = %d ' % balance_after)


