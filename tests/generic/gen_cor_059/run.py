from ten.test.basetest import TenNetworkTest
from ten.test.contracts.payable import ReceiveEther, SendEther
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network and deploy the contracts
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        balance = web3.eth.get_balance(account.address)
        self.log.info('Balance account %.6f ETH (%d Wei)', web3.from_wei(balance, 'ether'), balance)

        recv_contract = ReceiveEther(self, web3)
        recv_contract.deploy(network, account)

        send_contract = SendEther(self, web3)
        send_contract.deploy(network, account)

        # collect events
        recv_sub = AllEventsLogSubscriber(self, network, recv_contract.address, recv_contract.abi_path,
                                          stdout='recv_sub.out', stderr='recv_sub.err')
        recv_sub.run()

        send_sub = AllEventsLogSubscriber(self, network, send_contract.address, send_contract.abi_path,
                                          stdout='send_sub.out', stderr='send_sub.err')
        send_sub.run()

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
