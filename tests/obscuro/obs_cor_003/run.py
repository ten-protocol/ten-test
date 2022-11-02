import os
from pysys.constants import FAILED
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.relevancy.relevancy import Relevancy


class PySysTest(ObscuroTest):

    def execute(self):
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
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_http', network.connection_url(web_socket=False)])
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', contract.contract_address])
        args.extend(['--contract_abi', contract.abi_path])
        args.extend(['--pk_to_register', Properties().gameuserpk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscription confirmed', timeout=10)

        # perform some transactions as the game user, resulting in an event with the game user address included
        self.log.info('Performing transactions ... ')
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account, contract.GAS)

        # we would expect that given the game user vk is registered it can be decrypted
        try:
            self.waitForGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress', timeout=20)
        except:
            self.log.error('TImed out waiting for the event to be received')
            self.addOutcome(FAILED)
        else:
            self.assertGrep(file='subscriber.out', expr='Received event: CallerIndexedAddress')

