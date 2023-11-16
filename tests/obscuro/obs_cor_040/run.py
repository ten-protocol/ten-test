from ten.test.basetest import ObscuroNetworkTest
from ten.test.contracts.gas import GasConsumerAdd
from ten.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3_user, account_user = network.connect_account1(self)
        web3_hold, account_hold = network.connect(self, Properties().l2_gas_payment_account_pk(self.env), check_funds=False)

        contract_user = GasConsumerAdd(self, web3_user)
        contract_user.deploy(network, account_user)

        hold_balance_before = web3_hold.eth.get_balance(account_hold.address)
        user_balance_before = web3_user.eth.get_balance(account_user.address)

        est = contract_user.contract.functions.add_once().estimate_gas()
        self.log.info("Estimate add_once:   %d", est)

        tx = network.transact(self, web3_user, contract_user.contract.functions.add_once(), account_user, contract_user.GAS_LIMIT)

        user_balance_after = web3_user.eth.get_balance(account_user.address)
        hold_balance_after = web3_hold.eth.get_balance(account_hold.address)

        self.log.info("User account %s", account_user.address)
        self.log.info("User balance before:     %d", user_balance_before)
        self.log.info("User balance after:      %d", user_balance_after)
        self.log.info("User paid:               %d", (user_balance_before-user_balance_after))
        self.log.info("L2 fees:                 %d", int(tx["gasUsed"]))
        self.log.info("L1 fees:                 %d", (user_balance_before-user_balance_after)-int(tx["gasUsed"]))

        self.log.info("Hold account %s", account_hold.address)
        self.log.info("Hold balance before:     %d", hold_balance_before)
        self.log.info("Hold balance after:      %d", hold_balance_after)
        self.log.info("Hold balance difference: %d", (hold_balance_after-hold_balance_before))
