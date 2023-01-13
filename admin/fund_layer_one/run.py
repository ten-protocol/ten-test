from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):
    ETH = Web3().toWei(10, 'ether')
    TOKENS = Web3().toWei(500000, 'ether')
    TRANSFER_TOKENS = Web3().toWei(400000, 'ether')

    def execute(self):
        # connect to the L1 network and get contracts
        network = NetworkFactory.get_l1_network(self)
        hoc_address = Properties().l1_hoc_token_address(self.env)
        poc_address = Properties().l1_poc_token_address(self.env)
        bridge_address = Properties().management_bridge_address(self.env)
        web3_funded_l1, account_funded_l1 = network.connect(self, Properties().l1_funded_account_pk(self.env))
        web3_distro_l1, account_distro_l1 = network.connect(self, Properties().distro_account_pk(self.env))

        # fund eth to the distro account
        self.log.info('')
        self.log.info('Funding native ETH to the distro account')
        self.fund_eth(network, web3_funded_l1, account_funded_l1, web3_distro_l1, account_distro_l1, 10)

        if not self.is_obscuro_sim():
            # fund tokens on the ERC20s to the distro account from the funded account
            self.log.info('')
            self.log.info('Funding HOC and POC to the distro account')
            self.transfer_token(network, 'HOC', hoc_address, web3_funded_l1, account_funded_l1, account_distro_l1.address,
                                self.TOKENS, persist_nonce=False)
            self.transfer_token(network, 'POC', poc_address, web3_funded_l1, account_funded_l1, account_distro_l1.address,
                                self.TOKENS, persist_nonce=False)

            # fund tokens on the ERC20s to the bridge account from the distro account
            self.log.info('')
            self.log.info('Bridging HOC and POC to the distro account')
            self.transfer_token(network, 'HOC', hoc_address, web3_distro_l1, account_distro_l1, bridge_address,
                                self.TRANSFER_TOKENS, persist_nonce=False)
            self.transfer_token(network, 'POC', poc_address, web3_distro_l1, account_distro_l1, bridge_address,
                                self.TRANSFER_TOKENS, persist_nonce=False)
