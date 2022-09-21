import json, os
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    TOKEN_TARGET = 1000 * EthereumTest.ONE_GIGA

    def execute(self):
        # connect to the L1 network and get contracts
        network = NetworkFactory.get_l1_network(self.env)
        hoc_address = Properties().l1_hoc_token_address(self.env)
        poc_address = Properties().l1_poc_token_address(self.env)
        bridge_address = Properties().management_bridge_address(self.env)
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))

        # fund obx to the distro account
        self.fund_obx(network, web3_distro, account_distro)

        # fund tokens to the bridge account
        self.bridge_tokens(network, 'HOC', hoc_address, web3_distro, account_distro, bridge_address)
        self.bridge_tokens(network, 'POC', poc_address, web3_distro, account_distro, bridge_address)

    def bridge_tokens(self, network, token_name, token_address, web3_distro, account_distro, bridge_address):
        self.log.info('Running for token %s' % token_name)

        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'erc20', 'erc20.json')) as f:
            token = web3_distro.eth.contract(address=token_address, abi=json.load(f))

        distro_balance = token.functions.balanceOf(account_distro.address).call()
        self.log.info('  Token balance before;')
        self.log.info('    Distro balance = %d ' % distro_balance)

        network.transact(self, web3_distro, token.functions.transfer(bridge_address, distro_balance), account_distro, 7200000)

        distro_balance = token.functions.balanceOf(account_distro.address).call()
        self.log.info('  Token balance after;')
        self.log.info('    Distro balance = %d ' % distro_balance)

