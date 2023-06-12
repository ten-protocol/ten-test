from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3_1, account_1 = network.connect_account1(self)
        _, account_2 = network.connect_account2(self)

        balance_1 = web3_1.eth.get_balance(account_1.address)
        balance_2 = web3_1.eth.get_balance(account_2.address)
        self.log.info('Balance account 1 %.6f ETH (%d Wei)', web3_1.fromWei(balance_1, 'ether'), balance_1)
        self.log.info('Balance account 2 %.6f ETH (%d Wei)', web3_1.fromWei(balance_2, 'ether'), balance_2)

        self.send(network, web3_1, account_1, account_2.address, 0.01)

        balance_1 = web3_1.eth.get_balance(account_1.address)
        balance_2 = web3_1.eth.get_balance(account_2.address)
        self.log.info('Balance account 1 %.6f ETH (%d Wei)', web3_1.fromWei(balance_1, 'ether'), balance_1)
        self.log.info('Balance account 2 %.6f ETH (%d Wei)', web3_1.fromWei(balance_2, 'ether'), balance_2)

    def send(self, network, web3, account, address, amount):
        tx = {
            'to': address,
            'value': web3.toWei(amount, 'ether'),
            'gas': 72000,
            'gasPrice': web3.eth.gas_price
        }
        return network.tx(self, web3, tx, account)
