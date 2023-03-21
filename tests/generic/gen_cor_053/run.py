from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.contracts.payable import ReceiveEther, SendEther
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)
        balance = web3.eth.get_balance(account.address)
        self.log.info('Balance account %.3f' % web3.fromWei(balance, 'ether'))

        # deploy the contract and send eth to it
        recv_contract = ReceiveEther(self, web3)
        recv_contract.deploy(network, account)

        send_contract = SendEther(self, web3)
        send_contract.deploy(network, account)

        # collect events
        recv_sub = AllEventsLogSubscriber(self, network, recv_contract, stdout='recv_sub.out', stderr='recv_sub.err')
        recv_sub.run(Properties().account4pk(), network.connection_url(), network.connection_url(web_socket=True))

        send_sub = AllEventsLogSubscriber(self, network, send_contract, stdout='send_sub.out', stderr='send_sub.err')
        send_sub.run(Properties().account4pk(), network.connection_url(), network.connection_url(web_socket=True))

        # get balances and perform the transfer by encoding the function call
        balance1 = web3.eth.get_balance(recv_contract.address)
        self.log.info('Balance before %.3f' % web3.fromWei(balance1, 'ether'))

        data = send_contract.contract.encodeABI(fn_name='sendViaTransfer', args=[recv_contract.address])
        self.send(network, web3, send_contract, account, data, 0.5)

        balance2 = web3.eth.get_balance(recv_contract.address)
        self.log.info('Balance after %.3f' % web3.fromWei(balance2, 'ether'))

        # assert funds have gone to the contract
        self.assertTrue(web3.fromWei(balance2, 'ether') == 0.5)

    def send(self, network, web3, contract, account, data, amount):
        tx = {
            'value': web3.toWei(amount, 'ether'),
            'gas': contract.GAS_LIMIT,
            'data': data,
            'gasPrice': 1000,
            'to': contract.address
        }
        return network.tx(self, web3, tx, account)
