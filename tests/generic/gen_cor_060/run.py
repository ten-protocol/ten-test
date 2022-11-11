from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.erc20.obx import OBXCoin
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3_3, account3 = network.connect_account3(self, web_socket=self.WEBSOCKET)
        web3_2, account2 = network.connect_account2(self, web_socket=self.WEBSOCKET)
        web3_1, account1 = network.connect_account1(self, web_socket=self.WEBSOCKET)

        erc20 = OBXCoin(self, web3_1)
        erc20.deploy(network, account1)

        contract_1 = erc20.contract
        contract_2 = web3_2.eth.contract(address=erc20.contract_address, abi=erc20.abi)
        contract_3 = web3_3.eth.contract(address=erc20.contract_address, abi=erc20.abi)

        # check initial allocations
        self.log.info('Balances at initial allocation')
        self.log.info('  Account1 balance = %d ' % contract_1.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ' % contract_2.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ' % contract_3.functions.balanceOf(account3.address).call())
        self.assertTrue(contract_1.functions.balanceOf(account1.address).call() == 1000000)
        self.assertTrue(contract_2.functions.balanceOf(account2.address).call() == 0)
        self.assertTrue(contract_3.functions.balanceOf(account3.address).call() == 0)

        # transfer from account1 into account2
        network.transact(self, web3_1, erc20.contract.functions.transfer(account2.address, 200), account1, erc20.GAS)
        self.log.info('Balances after transfer from account 1 to account 2')
        self.log.info('  Account1 balance = %d ' % contract_1.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ' % contract_2.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ' % contract_3.functions.balanceOf(account3.address).call())
        self.assertTrue(contract_1.functions.balanceOf(account1.address).call() == 999800)
        self.assertTrue(contract_2.functions.balanceOf(account2.address).call() == 200)
        self.assertTrue(contract_3.functions.balanceOf(account3.address).call() == 0)

        # account1 approves account2 to withdraw 1000
        network.transact(self, web3_1, contract_1.functions.approve(account2.address, 1000), account1, erc20.GAS)

        # account2 withdraws from account1 into account3
        network.transact(self, web3_2, contract_2.functions.transferFrom(account1.address, account3.address, 100), account2, erc20.GAS)
        self.log.info('Balances after approval and transfer;')
        self.log.info('  Account1 balance = %d ' % contract_1.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ' % contract_2.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ' % contract_3.functions.balanceOf(account3.address).call())
        self.assertTrue(contract_1.functions.balanceOf(account1.address).call() == 999700)
        self.assertTrue(contract_2.functions.balanceOf(account2.address).call() == 200)
        self.assertTrue(contract_3.functions.balanceOf(account3.address).call() == 100)

        # account3 sends back to account1
        network.transact(self, web3_3, contract_3.functions.transfer(account1.address, 100), account3, erc20.GAS)
        self.log.info('Balances after transfer from account 3 to account 1')
        self.log.info('  Account1 balance = %d ' % contract_1.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ' % contract_2.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ' % contract_3.functions.balanceOf(account3.address).call())
        self.assertTrue(contract_1.functions.balanceOf(account1.address).call() == 999800)
        self.assertTrue(contract_2.functions.balanceOf(account2.address).call() == 200)
        self.assertTrue(contract_3.functions.balanceOf(account3.address).call() == 0)