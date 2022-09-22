from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    ETH_TARGET = 10 * EthereumTest.ONE_GIGA
    TOKEN_TARGET = 1000 * EthereumTest.ONE_GIGA

    def execute(self):
        # connect to the L1 network and get contracts
        network = NetworkFactory.get_l1_network(self.env)
        hoc_address = Properties().l1_hoc_token_address(self.env)
        poc_address = Properties().l1_poc_token_address(self.env)
        bridge_address = Properties().management_bridge_address(self.env)
        web3_funded, account_funded = network.connect(self, Properties().l1_funded_account_pk(self.env))
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))

        # fund eth to the distro account
        self.fund_eth(network, web3_funded, account_funded, web3_distro, account_distro)

        # fund tokens on the ERC20s to the distro account from the funded account
        self.transfer_token(network, 'HOC', hoc_address, web3_funded, account_funded, account_distro.address)
        self.transfer_token(network, 'POC', poc_address, web3_funded, account_funded, account_distro.address)

        # fund tokens on the ERC20s to the bridge account from the distro account
        self.transfer_token(network, 'HOC', hoc_address, web3_distro, account_distro, bridge_address, self.TOKEN_TARGET)
        self.transfer_token(network, 'POC', poc_address, web3_distro, account_distro, bridge_address, self.TOKEN_TARGET)

    def fund_eth(self, network, web3_funded, account_funded, web3_distro, account_distro):
        funded_eth = web3_funded.eth.get_balance(account_funded.address)
        distro_eth = web3_distro.eth.get_balance(account_distro.address)
        self.log.info('  ETH balance before;')
        self.log.info('    Funded balance = %d ' % funded_eth)
        self.log.info('    Distro balance = %d ' % distro_eth)

        if distro_eth < self.ETH_TARGET:
            amount = (self.ETH_TARGET - distro_eth)
            self.log.info('Below target so transferring %d' % amount)

            tx = {
                'chainId': network.chain_id(),
                'nonce': web3_funded.eth.get_transaction_count(account_funded.address),
                'to': account_distro.address,
                'value': amount,
                'gas': 4*21000,
                'gasPrice': web3_funded.eth.gas_price
            }
            tx_sign = account_funded.sign_transaction(tx)
            tx_hash = network.send_transaction(self, web3_funded, tx_sign)
            network.wait_for_transaction(self, web3_funded, tx_hash)

            funded_eth = web3_funded.eth.get_balance(account_funded.address)
            distro_eth = web3_distro.eth.get_balance(account_distro.address)
            self.log.info('  Eth balance after;')
            self.log.info('    Funded balance = %d ' % funded_eth)
            self.log.info('    Distro balance = %d ' % distro_eth)
