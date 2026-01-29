from ten.test.basetest import TenNetworkTest
from ten.test.contracts.weth import WETH
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        # run on the l1
        network = self.get_l1_network_connection()
        web3, account = network.connect_account1(self)
        address = web3.to_checksum_address(Properties().l1_weth_contract_address(self.env))
        self.run_for_network(network, web3, account, address, persist_nonce=False)

        # run on the l2
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        address = web3.to_checksum_address(Properties().l2_weth_contract_address(self.env))
        self.run_for_network(network, web3, account, address, persist_nonce=True)

    def run_for_network(self, network, web3, account, address, persist_nonce):
        # create an instance of the weth contract wrapper and check it is deployed
        weth = WETH(self, web3, address)
        self.log.info('Contract address is %s' % weth.address)

        code = web3.eth.get_code(weth.address)
        self.log.info("Contract bytecode length: %d", len(code))
        if code == b'' or code == '0x' or len(code) == 0:
            self.log.info("No contract code at that address — address wrong or contract not deployed.")

        initial_supply = weth.contract.functions.totalSupply().call()
        initial_balance = weth.contract.functions.balanceOf(account.address).call()
        self.log.info('Initial supply is %d' % initial_supply)
        self.log.info('Initial balance is %d' % initial_balance)

        # deposit eth
        network.transact(self, web3, weth.contract.functions.deposit(), account, weth.GAS_LIMIT, persist_nonce=persist_nonce, value=100)
        deposit_balance = weth.contract.functions.balanceOf(account.address).call()
        self.log.info('After deposit balance is %d' % deposit_balance)
        self.assertTrue(deposit_balance-initial_balance == 100, assertMessage='Balance should increase by 100')

        # withdraw eth
        network.transact(self, web3, weth.contract.functions.withdraw(10), account, weth.GAS_LIMIT, persist_nonce=persist_nonce)
        withdraw_balance = weth.contract.functions.balanceOf(account.address).call()
        self.log.info('After withdrawal balance is %d' % withdraw_balance)
        self.assertTrue(withdraw_balance-deposit_balance == -10, assertMessage='Balance should decrease by 10')

        # total supply
        final_supply = weth.contract.functions.totalSupply().call()
        self.log.info('Final supply is %d' % final_supply)
        self.assertTrue(final_supply-initial_supply == 90, assertMessage='Total supply should increase by 90')