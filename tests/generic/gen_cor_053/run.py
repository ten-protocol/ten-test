from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.payable import ReceiveEther, SendEther
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        balance = web3.eth.get_balance(account.address)
        self.log.info('Balance account %.6f ETH (%d Wei)', web3.fromWei(balance, 'ether'), balance)

        # deploy the contract and send eth to it
        recv_contract = ReceiveEther(self, web3)
        recv_contract.deploy(network, account)

        send_contract = SendEther(self, web3)
        send_contract.deploy(network, account)

        # collect events
        recv_sub = AllEventsLogSubscriber(self, network, recv_contract, stdout='recv_sub.out', stderr='recv_sub.err')
        recv_sub.run(None, network.connection_url(), network.connection_url(web_socket=True))

        send_sub = AllEventsLogSubscriber(self, network, send_contract, stdout='send_sub.out', stderr='send_sub.err')
        send_sub.run(None, network.connection_url(), network.connection_url(web_socket=True))

        # perform transfers
        last_balance = 0
        for fn in ['sendViaTransfer', 'sendViaSend', 'sendViaCall']:
            self.log.info('Encoding and transferring using %s', fn)

            data = send_contract.contract.encodeABI(fn_name=fn, args=[recv_contract.address])
            self.send(network, web3, send_contract, account, data, 100)

            balance = web3.eth.get_balance(recv_contract.address)
            self.log.info('Last balance: %s', last_balance)
            self.log.info('New balance : %s', balance)

            self.assertTrue(balance == last_balance + 100)
            last_balance = balance

    def send(self, network, web3, contract, account, data, amount):
        tx = {
            'value': amount,
            'gas': contract.GAS_LIMIT,
            'data': data,
            'gasPrice': web3.eth.gas_price,
            'to': contract.address
        }
        return network.tx(self, web3, tx, account)
