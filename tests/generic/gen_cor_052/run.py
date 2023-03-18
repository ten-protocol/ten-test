from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.contracts.payable import ReceiveEther
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)
        balance = web3.eth.get_balance(account.address)
        self.log.info('Balance account %.3f' % web3.fromWei(balance, 'ether'))

        # deploy the contract and send eth to it
        contract = ReceiveEther(self, web3)
        contract.deploy(network, account)

        # run a background script to filter and collect events
        subscriber = AllEventsLogSubscriber(self, network, contract)
        subscriber.run(Properties().account4pk(), network.connection_url(), network.connection_url(web_socket=True))

        # get balances and perform the transfer
        balance1 = web3.eth.get_balance(contract.address)
        self.log.info('Balance before %.3f' % web3.fromWei(balance1, 'ether'))

        self.send(network, web3, account, contract.address, 0.5)
        balance2 = web3.eth.get_balance(contract.address)
        self.log.info('Balance after %.3f' % web3.fromWei(balance2, 'ether'))

        # assert funds have gone to the contract
        self.assertTrue(web3.fromWei(balance2, 'ether') == 0.5)

    def send(self, network, web3, account, address, amount):
        tx = {
            'to': address,
            'value': web3.toWei(amount, 'ether'),
            'gas': 4*72000,
            'gasPrice': web3.eth.gas_price
        }
        return network.tx(self, web3, tx, account)
