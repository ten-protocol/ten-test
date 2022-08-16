from ethsys.basetest import EthereumTest
from ethsys.contracts.erc20.obx import OBXCoin
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self)
        web3_3, account3 = network.connect_account3()
        web3_2, account2 = network.connect_account2()
        web3_1, account1 = network.connect_account1()

        erc20 = OBXCoin(self, web3_1)
        erc20.deploy(network, account1)

        # check initial allocations
        self.log.info('Balances at initial allocation')
        self.log.info('  Account1 balance = %d ' % erc20.contract.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ' % erc20.contract.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ' % erc20.contract.functions.balanceOf(account3.address).call())
        self.assertTrue(erc20.contract.functions.balanceOf(account1.address).call() == 1000000)
        self.assertTrue(erc20.contract.functions.balanceOf(account2.address).call() == 0)
        self.assertTrue(erc20.contract.functions.balanceOf(account3.address).call() == 0)

        # transfer from account1 into account2
        network.transact(self, web3_1, erc20.contract.functions.transfer(account2.address, 200), account1, erc20.GAS)
        self.log.info('Balances after transfer from account 1 to account 2')
        self.log.info('  Account1 balance = %d ' % erc20.contract.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ' % erc20.contract.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ' % erc20.contract.functions.balanceOf(account3.address).call())
        self.assertTrue(erc20.contract.functions.balanceOf(account1.address).call() == 999800)
        self.assertTrue(erc20.contract.functions.balanceOf(account2.address).call() == 200)
        self.assertTrue(erc20.contract.functions.balanceOf(account3.address).call() == 0)

        # account1 approves account2 to withdraw 1000
        network.transact(self, web3_1, erc20.contract.functions.approve(account2.address, 1000), account1, erc20.GAS)

        # account2 withdraws from account1 into account3
        network.transact(self, web3_2, erc20.contract.functions.transferFrom(account1.address, account3.address, 100), account2, erc20.GAS)
        self.log.info('Balances after approval and transfer;')
        self.log.info('  Account1 balance = %d ' % erc20.contract.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ' % erc20.contract.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ' % erc20.contract.functions.balanceOf(account3.address).call())
        self.assertTrue(erc20.contract.functions.balanceOf(account1.address).call() == 999700)
        self.assertTrue(erc20.contract.functions.balanceOf(account2.address).call() == 200)
        self.assertTrue(erc20.contract.functions.balanceOf(account3.address).call() == 100)

        # account3 sends back to account1
        network.transact(self, web3_3, erc20.contract.functions.transfer(account1.address, 100), account3, erc20.GAS)
        self.log.info('Balances after transfer from account 3 to account 1')
        self.log.info('  Account1 balance = %d ' % erc20.contract.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ' % erc20.contract.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ' % erc20.contract.functions.balanceOf(account3.address).call())
        self.assertTrue(erc20.contract.functions.balanceOf(account1.address).call() == 999800)
        self.assertTrue(erc20.contract.functions.balanceOf(account2.address).call() == 200)
        self.assertTrue(erc20.contract.functions.balanceOf(account3.address).call() == 0)