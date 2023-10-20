from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.payable import ReceiveEther
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        balance = web3.eth.get_balance(account.address)
        self.log.info('Balance account %.6f ETH (%d Wei)', web3.fromWei(balance, 'ether'), balance)

        # deploy the contract and send eth to it
        contract = ReceiveEther(self, web3)
        contract.deploy(network, account)

        # run a background script to filter and collect events
        subscriber = AllEventsLogSubscriber(self, network, contract.address, contract.abi_path)
        subscriber.run()

        # get balances and perform the transfer
        balance1 = web3.eth.get_balance(contract.address)
        self.log.info('Balance account before %.6f ETH (%d Wei)', web3.fromWei(balance1, 'ether'), balance1)

        tx_receipt = self.send(network, web3, account, contract.address, 10)
        self.log.info('Gas used = %d Wei', tx_receipt.gasUsed)
        balance2 = web3.eth.get_balance(contract.address)
        self.log.info('Balance account after %.6f ETH (%d Wei)', web3.fromWei(balance2, 'ether'), balance2)

        # assert funds have gone to the contract
        self.assertTrue(balance2 == 10)

    def send(self, network, web3, account, address, amount):
        gpv = (4*72000*web3.eth.gas_price) + amount
        self.log.info('Gas * price + value == %0.6f', web3.fromWei(gpv, 'ether'))
        tx = {
            'to': address,
            'value': amount,
            'gas': 72000,
            'gasPrice': web3.eth.gas_price
        }
        return network.tx(self, web3, tx, account)
