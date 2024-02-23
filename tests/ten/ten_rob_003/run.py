import secrets, random, time
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage
from ten.test.helpers.wallet_extension import WalletExtension
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):
    CLIENTS = 100
    TRANSACTIONS = 10

    def execute(self):
        # get the main connection through the primary gateway
        network_connection_primary = self.get_network_connection()
        web3_1, account_1 = network_connection_primary.connect_account1(self)

        # deploy a contract that emits a lifecycle event on calling a specific method as a transaction
        storage_1 = Storage(self, web3_1, 100)
        storage_1.deploy(network_connection_primary, account_1)

        # make a subscription for all events to the contract
        subscriber_1 = AllEventsLogSubscriber(self, network_connection_primary, storage_1.address, storage_1.abi_path,
                                              stdout='subscriber.out',
                                              stderr='subscriber.err')
        subscriber_1.run()

        # register, or join and register all the clients
        connections = []
        primary_userid = 1
        additional_userid = 0
        for i in range(0, self.CLIENTS):
            pk = secrets.token_hex(32)
            if random.randint(0, 8) < 4:
                additional_userid = additional_userid + 1
                self.log.info('Registering client %d with new user id (current total %d)', i, additional_userid)
                network_connection = self.get_network_connection()
            else:
                primary_userid = primary_userid + 1
                self.log.info('Registering client %d with primary user id (current total %d)', i, primary_userid)
                network_connection = network_connection_primary
            web3, account = network_connection.connect(self, private_key=pk, check_funds=False)
            storage = Storage.clone(web3, account, storage_1)
            connections.append((web3, account, network_connection, storage))
            time.sleep(0.05)

        self.log.info('Number registrations on primary user id = %d', primary_userid)
        self.log.info('Number registrations on unique user id = %d', additional_userid)

        # perform some randon client transactions
        count = 0
        for i in range(0, self.TRANSACTIONS):
            count = count + 1
            web3, account, network_connection, storage = random.choice(connections)
            self.distribute_native(account, network_connection.ETH_ALLOC_EPHEMERAL)
            network_connection.transact(self, web3, storage.contract.functions.store(count), account, storage.GAS_LIMIT)

        self.waitForSignal(file='subscriber.out', expr='Received event: Stored', condition='==%d' % self.TRANSACTIONS, timeout=120)
        self.assertLineCount(file='subscriber.out', expr='Received event: Stored', condition='==%d' % self.TRANSACTIONS)