import secrets
from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import Relevancy
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber

class PySysTest(TenNetworkTest):

    def execute(self):
        # account 1 through one gateway (seen, has tx'd before)
        network_1 = self.get_network_connection(name='account1')
        web3_1, account_1 = network_1.connect_account1(self)

        # account 2 through another gateway (seen, has tx'd before)
        network_2 = self.get_network_connection(name='account2')
        web3_2, account_2 = network_2.connect_account2(self)

        # account 3 is ephemeral, never seen, never transacted
        unseen = '0x0000000000000000000000000000000000000001'

        # deploy the storage contract using account 1, and get a handle to it for account 2
        contract_1 = Relevancy(self, web3_1)
        contract_1.deploy(network_1, account_1)
        contract_2 = Relevancy.clone(web3_2, account_2, contract_1)

        # subscribe for events from the contract through gateway account 1 is using
        self.subscribe(network_1, contract_1.address, contract_1.abi_path)

        # account 2 transacts, passing an indexed account address of the unseen account, and then transacts again
        # using the account address of the seen account (account 1)
        network_2.transact(self, web3_2, contract_2.contract.functions.indexedAddressAndNumber(unseen), account_2, contract_2.GAS_LIMIT)
        network_2.transact(self, web3_2, contract_2.contract.functions.indexedAddressAndNumber(account_1.address), account_2, contract_2.GAS_LIMIT)

        # account 1 transacts, passing an indexed account address of the unseen account, and then transacts again
        # using the account address of the seen account (account 2)
        network_1.transact(self, web3_1, contract_1.contract.functions.indexedAddressAndNumber(unseen), account_1, contract_2.GAS_LIMIT)
        network_1.transact(self, web3_1, contract_1.contract.functions.indexedAddressAndNumber(account_2.address), account_1, contract_1.GAS_LIMIT)

    def subscribe(self, network, address, abi_path):
        subscriber = AllEventsLogSubscriber(self, network, address, abi_path, stdout='subscriber.out', stderr='subscriber.err')
        subscriber.run()