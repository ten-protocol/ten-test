from pysys.constants import FAILED
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.contracts.relevancy import Relevancy
from obscuro.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)

        # connect via the primary wallet extension used by the test in the order of
        # account1, account2, account3, account4
        web3, account = network.connect_account4(self)
        network.connect_account1(self)
        network.connect_account2(self)
        network.connect_account3(self)

        # deploy the storage contract as account 4
        contract = Relevancy(self, web3)
        contract.deploy(network, account)

        # run a background script to filter and collect events
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            filter_address=contract.address,
            filter_topics=[
                web3.keccak(text='CallerIndexedAddress(address)').hex(),
                '0x'+(24*'0')+str(account.address.split('0x')[1])
            ]
        )
        subscriber.subscribe()

        # perform some transactions as account4, resulting in an event with the account 4 address included
        self.log.info('Performing transactions ... ')
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account, contract.GAS_LIMIT)
        self.wait(float(self.block_time)*1.1)

        # we would expect that given account4 vk is registered it can be decrypted
        try:
            self.waitForGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress', timeout=10)
        except:
            self.log.error('Timed out waiting for CallerIndexedAddress event log in subscriber')
            self.addOutcome(FAILED)
        else:
            self.assertGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress')

