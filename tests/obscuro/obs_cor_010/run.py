import secrets
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroTest):

    def execute(self):
        network = Obscuro
        web3_distro, account_distro = network.connect(self, Properties().distro_account_pk(self.env))
        hoc_address_l1 = Properties().l1_hoc_token_address(self.env)
        hoc_address_l2 = Properties().l2_hoc_token_address(self.env)

        private_key = secrets.token_hex(32)
        web3_user, account_user = network.connect(self, private_key)
        self.fund_eth(network, web3_distro, account_distro, web3_user, account_user)

    def fund_eth(self, network, web3_from, account_from, web3_to, account_to):
        from_eth = web3_from.eth.get_balance(account_from.address)
        to_eth = web3_to.eth.get_balance(account_to.address)
        self.log.info('ETH balance before;')
        self.log.info('  Distro balance = %f ' % web3_from.fromWei(from_eth, 'ether'))
        self.log.info('  User balance = %f ' % web3_to.fromWei(to_eth, 'ether'))

        tx = {
            'chainId': network.chain_id(),
            'nonce': web3_from.eth.get_transaction_count(account_from.address),
            'to': account_to.address,
            'value': web3_from.toWei(0.5, 'ether'),
            'gas': 4*21000,
            'gasPrice': web3_from.eth.gas_price
        }
        tx_sign = account_from.sign_transaction(tx)
        tx_hash = network.send_transaction(self, web3_from, tx_sign)
        network.wait_for_transaction(self, web3_from, tx_hash)

        from_eth = web3_from.eth.get_balance(account_from.address)
        to_eth = web3_to.eth.get_balance(account_to.address)
        self.log.info('ETH balance after;')
        self.log.info('  Distro balance = %f ' % web3_from.fromWei(from_eth, 'ether'))
        self.log.info('  User balance = %f ' % web3_to.fromWei(to_eth, 'ether'))
