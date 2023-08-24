from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.helpers.wallet_extension import WalletExtension
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
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

        # make a subscription for all events to the contract, one through each of the connections
        subscriber_1 = AllEventsLogSubscriber(self, network_connection_1, storage,
                                              stdout='subscriber_1.out',
                                              stderr='subscriber_2.err')
        subscriber_1.run()

        subscriber_2 = AllEventsLogSubscriber(self, network_connection_2, storage,
                                              stdout='subscriber_2.out',
                                              stderr='subscriber_2.err')
        subscriber_2.run()

        # each account performs a transaction against the storage contract which results in a lifecycle
        # event being emitted
        count = 0
        for (web3, account, network) in [(web3_1, account_1, network_connection_1),
                                         (web3_2, account_2, network_connection_1),
                                         (web3_3, account_3, network_connection_2),
                                         (web3_4, account_4, network_connection_2)]:
            count = count + 1
            network.transact(self, web3, storage.contract.functions.store(count), account, storage.GAS_LIMIT)

        self.waitForSignal(file='subscriber_1.out', expr='Received event: Stored', condition='==4', timeout=10)
        self.waitForSignal(file='subscriber_1.out', expr='Received event: Stored', condition='==4', timeout=10)

        expr_list = []
        expr_list.append('Received event: Stored')
        expr_list.append('returnValues: Result.*value: \'1\'')
        expr_list.append('Received event: Stored')
        expr_list.append('returnValues: Result.*value: \'2\'')
        expr_list.append('Received event: Stored')
        expr_list.append('returnValues: Result.*value: \'3\'')
        expr_list.append('Received event: Stored')
        expr_list.append('returnValues: Result.*value: \'4\'')
        self.assertOrderedGrep(file='subscriber_1.out', exprList=expr_list)
        self.assertOrderedGrep(file='subscriber_2.out', exprList=expr_list)
        self.assertLineCount(file='subscriber_1.out', expr='Received event: Stored', condition='==4')
        self.assertLineCount(file='subscriber_2.out', expr='Received event: Stored', condition='==4')