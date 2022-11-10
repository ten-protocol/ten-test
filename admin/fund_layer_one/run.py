from obscuro.test.basetest import ObscuroTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroTest):
    ETH = 10 * ObscuroTest.ONE_GIGA
    TOKENS = 5000000 * ObscuroTest.ONE_GIGA
    TRANSFER_TOKENS = 4000000 * ObscuroTest.ONE_GIGA

    def execute(self):
        # connect to the L1 network and get contracts
        network = NetworkFactory.get_l1_network(self.env)
        hoc_address = Properties().l1_hoc_token_address(self.env)
        poc_address = Properties().l1_poc_token_address(self.env)
        bridge_address = Properties().management_bridge_address(self.env)
        web3_funded, account_funded = network.connect(self, Properties().l1_funded_account_pk(self.env))
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))

        # fund eth to the distro account
        self.log.info('')
        self.log.info('Funding native ETH to the distro account')
        self.fund_eth(network, web3_funded, account_funded, web3_distro, account_distro, 10)

        if not self.is_obscuro_sim():
            # fund tokens on the ERC20s to the distro account from the funded account
            self.log.info('')
            self.log.info('Funding HOC and POC to the distro account')
            self.transfer_token(network, 'HOC', hoc_address, web3_funded, account_funded, account_distro.address, self.TOKENS)
            self.transfer_token(network, 'POC', poc_address, web3_funded, account_funded, account_distro.address, self.TOKENS)

            # fund tokens on the ERC20s to the bridge account from the distro account
            self.log.info('')
            self.log.info('Bridging HOC and POC to the distro account')
            self.transfer_token(network, 'HOC', hoc_address, web3_distro, account_distro, bridge_address, self.TRANSFER_TOKENS)
            self.transfer_token(network, 'POC', poc_address, web3_distro, account_distro, bridge_address, self.TRANSFER_TOKENS)
