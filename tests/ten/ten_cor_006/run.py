from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import Relevancy
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()

        # connect via the primary wallet extension used by the test in the order of
        # account4, account1, account2, account3
        web3_4, account4 = network.connect_account4(self)
        network.connect_account1(self)
        network.connect_account2(self)
        network.connect_account3(self)

        # deploy the storage contract as account 4 and get references to it for each account
        contract_4 = Relevancy(self, web3_4)
        contract_4.deploy(network, account4)

        # run a background script to filter and collect events (called by account 4)
        subscriber = AllEventsLogSubscriber(self, network, contract_4.address, contract_4.abi_path,
                                            stdout='subscriber.out',
                                            stderr='subscriber.err')
        subscriber.run()
        self.wait(float(self.block_time)*1.1)

        # perform a transaction
        self.log.info('Performing transactions ... ')
        network.transact(self, web3_4, contract_4.contract.functions.nonIndexedAddressAndNumber(account4.address),
                         account4, contract_4.GAS_LIMIT)
        self.wait(float(self.block_time)*1.1)

        # wait and assert that all accounts receive their own events
        self.waitForGrep(file='subscriber.out', expr='Received event: NonIndexedAddressAndNumber', timeout=90)
        self.assertLineCount(file='subscriber.out', expr='Received event: NonIndexedAddressAndNumber', condition='==1')


