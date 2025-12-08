from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import Relevancy
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network on the primary gateway
        network = self.get_network_connection()

        # connect via the primary gateway used by the test in the order of
        # account4, account1, account2, account3 (all use the same token)
        web3_4, account4 = network.connect_account4(self)
        web3_1, account1 = network.connect_account1(self)
        web3_2, account2 = network.connect_account2(self)
        web3_3, account3 = network.connect_account3(self)

        # deploy the storage contract as account 4 and get references to it for each account
        contract_4 = Relevancy(self, web3_4)
        contract_4.deploy(network, account4)
        contract_1 = Relevancy.clone(web3_1, account1, contract_4)
        contract_2 = Relevancy.clone(web3_2, account2, contract_4)
        contract_3 = Relevancy.clone(web3_3, account3, contract_4)

        # run a background script to filter and collect events (called by account 4)
        subscriber = AllEventsLogSubscriber(self, network, contract_4.address, contract_4.abi_path,
                                            stdout='subscriber.out',
                                            stderr='subscriber.err')
        subscriber.run()
        self.wait(float(self.block_time)*1.1)

        # perform some transactions
        self.log.info('Performing transactions ... ')
        network.transact(self, web3_4, contract_4.contract.functions.callerIndexedAddress(), account4, contract_4.GAS_LIMIT)
        network.transact(self, web3_1, contract_1.contract.functions.callerIndexedAddress(), account1, contract_1.GAS_LIMIT)
        network.transact(self, web3_2, contract_2.contract.functions.callerIndexedAddress(), account2, contract_2.GAS_LIMIT)
        network.transact(self, web3_3, contract_3.contract.functions.callerIndexedAddress(), account3, contract_3.GAS_LIMIT)
        self.wait(float(self.block_time)*1.1)

        # wait and assert that all accounts receive their own events
        self.waitForGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress', condition='==4', timeout=30)
        self.assertLineCount(file='subscriber.out', expr='Received event: CallerIndexedAddress', condition='==4')


