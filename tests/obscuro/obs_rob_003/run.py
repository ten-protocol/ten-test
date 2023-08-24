import secrets, random
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.helpers.wallet_extension import WalletExtension
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # start a single wallet extension
        wallet = WalletExtension.start(self, name='shared')
        network_connection_primary = self.get_network_connection(wallet=wallet)
        web3_1, account_1 = network_connection_primary.connect_account1(self)

        # deploy a contract that emits a lifecycle event on calling a specific method as a transaction
        storage = Storage(self, web3_1, 100)
        storage.deploy(network_connection_primary, account_1)

        # make a subscription for all events to the contract, one through each of the connections
        subscriber_1 = AllEventsLogSubscriber(self, network_connection_primary, storage,
                                              stdout='subscriber.out',
                                              stderr='subscriber.err')
        subscriber_1.run()

        # each account performs a transaction against the storage contract which results in a lifecycle
        # event being emitted
        count = 0
        connections = []
        primary_userid = 1
        additional_userid = 0
        for i in range(0, 500):
            self.log.info('')
            pk = secrets.token_hex(32)
            if random.randint(0, 4) < 3:
                additional_userid = additional_userid + 1
                self.log.info('Registering client %d with new user id (current total %d)', i, additional_userid)
                network_connection = self.get_network_connection(wallet=wallet)
            else:
                primary_userid = primary_userid + 1
                self.log.info('Registering client %d with primary user id (current total %d)', i, primary_userid)
                network_connection = network_connection_primary
            web3, account = network_connection.connect(self, private_key=pk, check_funds=False)
            connections.append((web3, account, network_connection))
            self.wait(0.1)

        self.log.info('Number registrations on primary user id = %d', primary_userid)
        self.log.info('Number registrations on unique user id = %d', additional_userid)
        web3, account, network_connection = random.choice(connections)
        self.distribute_native(account, 0.01)
        network_connection.transact(self, web3, storage.contract.functions.store(count), account, storage.GAS_LIMIT)
        self.waitForSignal(file='subscriber.out', expr='Received event: Stored', condition='==1', timeout=10)
        self.assertGrep(file='subscriber.out', expr='Received event: Stored')