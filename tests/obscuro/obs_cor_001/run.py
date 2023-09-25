from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.payable import ReceiveEther


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # the deployer goes through the test wallet extension
        network_deploy = self.get_network_connection()
        web3_deploy, account_deploy = network_deploy.connect_account1(self)

        # the user goes through their own instance of the wallet extension
        network_user = self.get_network_connection(name='user')
        web3_user, account_user = network_user.connect_account2(self)

        # deploy the contract and send eth to it
        contract = ReceiveEther(self, web3_deploy)
        contract.deploy(network_deploy, account_deploy)
        self.send(network_user, web3_user, account_user, contract, 0.001)

        # the user should not be able to read the balance of the contract
        raised = False
        try:
            balance = web3_user.eth.get_balance(contract.address)
            self.log.info('Contract balance is %.3f', web3_user.fromWei(balance, 'ether'))
        except Exception as e:
            raised = True
        self.assertTrue(raised)

        # the deployer should still be able to read their balance
        balance = web3_deploy.eth.get_balance(contract.address)
        self.log.info('Contract balance is %.3f', web3_deploy.fromWei(balance, 'ether'))
        self.assertTrue(balance == web3_deploy.toWei(0.001, 'ether'))

    def send(self, network, web3, account, contract, amount):
        tx = {
            'to': contract.address,
            'value': web3.toWei(amount, 'ether'),
            'gas': contract.GAS_LIMIT,
            'gasPrice': web3.eth.gas_price
        }
        return network.tx(self, web3, tx, account)
