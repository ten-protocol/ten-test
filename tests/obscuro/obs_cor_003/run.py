import os
from pysys.constants import FAILED
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.relevancy.relevancy import Relevancy
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber

class PySysTest(ObscuroTest):

    def execute(self):
        block_time=Properties().block_time_secs(self.env)

        # connect to network
        network = Obscuro

        # connect via the primary wallet extension used by the test in the order of
        # account1, account2, account3, game user
        network.connect_account1(self)
        network.connect_account2(self)
        network.connect_account1(self)
        web3, account = network.connect_game_user(self)

        # deploy the storage contract
        contract = Relevancy(self, web3)
        contract.deploy(network, account)

        # run a background script to filter and collect events (this is not tied to any account)
        subscriber = AllEventsLogSubscriber(self, network, contract)
        subscriber.run(Properties().gameuserpk(), network.connection_url(), network.connection_url(web_socket=True))

        # perform some transactions as the game user, resulting in an event with the game user address included
        self.log.info('Performing transactions ... ')
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account, contract.GAS)
        self.wait(float(block_time)*1.1)

        # we would expect that given the game user vk is registered it can be decrypted
        try:
            self.waitForGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress', timeout=block_time)
        except:
            self.log.error('TImed out waiting for CallerIndexedAddress event log in subscriber')
            self.addOutcome(FAILED)
        else:
            self.assertGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress')

