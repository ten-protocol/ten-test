import os
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.helpers.wallet_extension import WalletExtension
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.

        # start a single wallet extension
        wallet = WalletExtension.start(self, name='shared')

        # create two connections, each with their own user id (via a join call)
        network_connection_1 = self.get_network_connection(wallet=wallet)
        network_connection_2 = self.get_network_connection(wallet=wallet)

        # each user id has two registered accounts made against it
        web3_1, account_1 = network_connection_1.connect_account1(self)
        web3_2, account_2 = network_connection_1.connect_account2(self)
        web3_3, account_3 = network_connection_2.connect_account3(self)
        web3_4, account_4 = network_connection_2.connect_account4(self)

        # deploy a contract that emits a lifecycle event on calling a specific method as a transaction
        storage = Storage(self, web3_1, 100)
        storage.deploy(network_connection_1, account_1)

        # make a subscription for all event logs, one through each of the connections
        self.subscribe(network_connection_1, 'one')
        self.subscribe(network_connection_2, 'two')

        # each account performs a transaction against the storage contract which results in a lifecycle
        # event being emitted
        count = 0
        for (web3, account, network) in [(web3_1, account_1, network_connection_1),
                                         (web3_2, account_2, network_connection_1),
                                         (web3_3, account_3, network_connection_2),
                                         (web3_4, account_4, network_connection_2)]:
            count = count + 1
            network.transact(self, web3, storage.contract.functions.store(count), account, storage.GAS_LIMIT)

        self.wait(10.0)

    def subscribe(self, network, name):
        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber_%s.out' % name)
        stderr = os.path.join(self.output, 'subscriber_%s.err' % name)
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscribed for event logs', timeout=10)