from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.erc20 import MintedERC20Token


class PySysTest(GenericNetworkTest):

    def execute(self):
        decimals = (10 ** 18)
        # deployment of contract
        network = self.get_network_connection()
        web3_3, account3 = network.connect_account3(self)
        web3_2, account2 = network.connect_account2(self)
        web3_1, account1 = network.connect_account1(self)

        erc20 = MintedERC20Token(self, web3_1, 'OBXCoin', 'OBX', 1000000 * decimals)
        erc20.deploy(network, account1)

        contract_1 = erc20.contract
        contract_2 = web3_2.eth.contract(address=erc20.address, abi=erc20.abi)
        contract_3 = web3_3.eth.contract(address=erc20.address, abi=erc20.abi)

        # check initial allocations
        self.log.info('Balances at initial allocation')
        self.log.info('  Account1 balance = %d ', contract_1.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ', contract_2.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ', contract_3.functions.balanceOf(account3.address).call())
        self.assertTrue(contract_1.functions.balanceOf(account1.address).call() == 1000000 * decimals)
        self.assertTrue(contract_2.functions.balanceOf(account2.address).call() == 0)
        self.assertTrue(contract_3.functions.balanceOf(account3.address).call() == 0)

        # transfer from account1 into account2
        network.transact(self, web3_1, erc20.contract.functions.transfer(account2.address, 200 * decimals), account1, erc20.GAS_LIMIT)
        self.log.info('Balances after transfer from account 1 to account 2')
        self.log.info('  Account1 balance = %d ', contract_1.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ', contract_2.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ', contract_3.functions.balanceOf(account3.address).call())
        self.assertTrue(contract_1.functions.balanceOf(account1.address).call() == 999800 * decimals)
        self.assertTrue(contract_2.functions.balanceOf(account2.address).call() == 200 * decimals)
        self.assertTrue(contract_3.functions.balanceOf(account3.address).call() == 0)

        # account1 approves account2 to withdraw 1000
        network.transact(self, web3_1, contract_1.functions.approve(account2.address, 1000 * decimals), account1, erc20.GAS_LIMIT)

        # account2 withdraws from account1 into account3
        network.transact(self, web3_2, contract_2.functions.transferFrom(account1.address, account3.address, 100 * decimals), account2, erc20.GAS_LIMIT)
        self.log.info('Balances after approval and transfer;')
        self.log.info('  Account1 balance = %d ', contract_1.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ', contract_2.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ', contract_3.functions.balanceOf(account3.address).call())
        self.assertTrue(contract_1.functions.balanceOf(account1.address).call() == 999700 * decimals)
        self.assertTrue(contract_2.functions.balanceOf(account2.address).call() == 200 * decimals)
        self.assertTrue(contract_3.functions.balanceOf(account3.address).call() == 100 * decimals)

        # account3 sends back to account1
        network.transact(self, web3_3, contract_3.functions.transfer(account1.address, 100 * decimals), account3, erc20.GAS_LIMIT)
        self.log.info('Balances after transfer from account 3 to account 1')
        self.log.info('  Account1 balance = %d ', contract_1.functions.balanceOf(account1.address).call())
        self.log.info('  Account2 balance = %d ', contract_2.functions.balanceOf(account2.address).call())
        self.log.info('  Account3 balance = %d ', contract_3.functions.balanceOf(account3.address).call())
        self.assertTrue(contract_1.functions.balanceOf(account1.address).call() == 999800 * decimals)
        self.assertTrue(contract_2.functions.balanceOf(account2.address).call() == 200 * decimals)
        self.assertTrue(contract_3.functions.balanceOf(account3.address).call() == 0)