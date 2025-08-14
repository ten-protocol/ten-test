from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.gas import GasConsumerAdd
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network on the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        gas_payment_address = Properties().l2_gas_payment_address(self.env)

        contract_user = GasConsumerAdd(self, web3)
        contract_user.deploy(network, account)

        hold_balance_before = web3.eth.get_balance(gas_payment_address)
        user_balance_before = web3.eth.get_balance(account.address)
        gas_price = web3.eth.gas_price

        est = contract_user.contract.functions.add_once().estimate_gas()
        self.log.info("Estimate add_once:   %d", est)

        tx = network.transact(self, web3, contract_user.contract.functions.add_once(), account, contract_user.GAS_LIMIT)

        hold_balance_after = web3.eth.get_balance(gas_payment_address)
        user_balance_after = web3.eth.get_balance(account.address)

        self.log.info("User account %s", account.address)
        self.log.info("User balance before:     %d", user_balance_before)
        self.log.info("User balance after:      %d", user_balance_after)
        self.log.info("User paid:               %d", (user_balance_before-user_balance_after))
        self.log.info("L2 fees:                 %d", int(tx["gasUsed"]*gas_price))
        self.log.info("L1 fees:                 %d", (user_balance_before-user_balance_after)-int(tx["gasUsed"])*gas_price)

        self.log.info("Hold account %s", gas_payment_address)
        self.log.info("Hold balance before:     %d", hold_balance_before)
        self.log.info("Hold balance after:      %d", hold_balance_after)
        self.log.info("Hold balance difference: %d", (hold_balance_after-hold_balance_before))

        self.assertTrue((user_balance_before-user_balance_after) == (hold_balance_after-hold_balance_before))