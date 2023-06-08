from pysys.constants import FAILED
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.contracts.relevancy import Relevancy
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)

        # connect via the primary wallet extension used by the test in the order of
        # account1, account2, account3, account4
        web3_4, account4 = network.connect_account4(self)
        web3_1, account1 = network.connect_account1(self)
        web3_2, account2 = network.connect_account2(self)
        web3_3, account3 = network.connect_account3(self)

        # deploy the storage contract as account 4
        contract = Relevancy(self, web3_4)
        contract.deploy(network, account4)

        # run a background script to filter and collect events
        subscriber = AllEventsLogSubscriber(self, network, contract,
                                            stdout='subscriber.out',
                                            stderr='subscriber.err')
        subscriber.run()

        # perform some transactions
        self.log.info('Performing transactions ... ')
        network.transact(self, web3_4, contract.contract.functions.callerIndexedAddress(), account4, contract.GAS_LIMIT)
        network.transact(self, web3_1, contract.contract.functions.callerIndexedAddress(), account1, contract.GAS_LIMIT)
        network.transact(self, web3_2, contract.contract.functions.callerIndexedAddress(), account2, contract.GAS_LIMIT)
        network.transact(self, web3_3, contract.contract.functions.callerIndexedAddress(), account3, contract.GAS_LIMIT)
        self.wait(float(self.block_time)*1.1)

        # wait and assert that account4 does see this event
        self.waitForGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress', timeout=90)
        self.assertLineCount(file='subscriber.out', expr='Received event: CallerIndexedAddress', condition='==1')


