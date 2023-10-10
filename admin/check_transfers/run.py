from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.networks.sepolia import Sepolia
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.erc20 import MintedERC20Token


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = Sepolia(self)
        web3_1, account1 = network.connect(self, private_key=Properties().fundacntpk(), check_funds=False)
        web3_2, account2 = network.connect_account1(self)

        erc20 = MintedERC20Token(self, web3_1, 'OBXCoin', 'OBX', 1000000)
        erc20.get_or_deploy(network, account1)

        contract_1 = erc20.contract
        contract_2 = web3_2.eth.contract(address=erc20.address, abi=erc20.abi)

        # check initial allocations
        balance1_before = contract_1.functions.balanceOf(account1.address).call()
        balance2_before = contract_2.functions.balanceOf(account2.address).call()
        self.log.info('Balances at initial allocation')
        self.log.info('  Account1 balance = %d ', balance1_before)
        self.log.info('  Account2 balance = %d ', balance2_before)

        # transfer from account1 into account2
        network.transact(self, web3_1, erc20.contract.functions.transfer(account2.address, 1), account1,
                         erc20.GAS_LIMIT)
        balance1_after = contract_1.functions.balanceOf(account1.address).call()
        balance2_after = contract_2.functions.balanceOf(account2.address).call()
        self.log.info('Balances after transfer from account 1 to account 2')
        self.log.info('  Account1 balance = %d ', balance1_after)
        self.log.info('  Account2 balance = %d ', balance2_after)

