from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.relevancy.relevancy import Relevancy
from obscuro.test.helpers.wallet_extension import WalletExtension
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # connect to network
        network = Obscuro
        web3, account = network.connect_account4(self)
        account1 = Web3().eth.account.privateKeyToAccount(Properties().account1pk())

        # deploy the storage contract
        contract = Relevancy(self, web3)
        contract.deploy(network, account)

        # run the javascript event log subscriber in the background for the other accounts
        self.subscribe(network, Properties().account4pk(), 'account4', contract)
        self.subscribe(network, Properties().account1pk(), 'account1', contract, new_wallet=True)
        self.subscribe(network, Properties().account2pk(), 'account2', contract, new_wallet=True)
        self.subscribe(network, Properties().account3pk(), 'account3', contract, new_wallet=True)

        # perform some transactions
        self.log.info('Performing transactions ... ')
        network.transact(self, web3,
                         contract.contract.functions.twoIndexedAddresses(account.address, account1.address),
                         account, contract.GAS_LIMIT)
        self.wait(float(self.block_time)*1.1)

        # wait and assert that account4 does see this event
        self.waitForGrep(file='subscriber_account4.out', expr='Received event: TwoIndexedAddresses', timeout=20)
        self.assertGrep(file='subscriber_account4.out', expr='Received event: TwoIndexedAddresses')

        # wait and assert that account1 does see this event
        self.waitForGrep(file='subscriber_account1.out', expr='Received event: TwoIndexedAddresses', timeout=20)
        self.assertGrep(file='subscriber_account1.out', expr='Received event: TwoIndexedAddresses')

        # assert that the other two users do not see the event
        self.assertGrep(file='subscriber_account2.out', expr='Received event: TwoIndexedAddresses', contains=False)
        self.assertGrep(file='subscriber_account3.out', expr='Received event: TwoIndexedAddresses', contains=False)

    def subscribe(self, network, pk_to_register, name, contract, new_wallet=False):
        network_http = network.connection_url(web_socket=False)
        network_ws = network.connection_url(web_socket=True)

        # if going through a new wallet, start up and reassign the connection URLS from the default
        if new_wallet:
            http_port = self.getNextAvailableTCPPort()
            ws_port = self.getNextAvailableTCPPort()
            network_http = 'http://127.0.0.1:%d' % http_port
            network_ws = 'ws://127.0.0.1:%d' % ws_port
            extension = WalletExtension(self, http_port, ws_port, name=name)
            extension.run()

        # run a background script to filter and collect events
        subscriber = AllEventsLogSubscriber(self, network, contract,
                                            stdout='subscriber_%s.out' % name,
                                            stderr='subscriber_%s.err' % name)
        subscriber.run(pk_to_register, network_http, network_ws)
