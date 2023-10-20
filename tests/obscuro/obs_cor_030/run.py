from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.helpers.wallet_extension import WalletExtension
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        # start a single wallet extension
        wallet = WalletExtension.start(self, name='shared')

        # create two connections, each with their own user id (via a join call)
        self.log.info('')
        self.log.info('Create two user_id connections through a single wallet extension')
        network_connection_1 = self.get_network_connection(wallet=wallet)
        network_connection_2 = self.get_network_connection(wallet=wallet)

        # each user id has two registered accounts made against it
        self.log.info('')
        self.log.info('Register two accounts with each of the user_id connections')
        web3_1, account_1 = network_connection_1.connect_account1(self)
        web3_2, account_2 = network_connection_1.connect_account2(self)
        web3_3, account_3 = network_connection_2.connect_account3(self)
        web3_4, account_4 = network_connection_2.connect_account4(self)

        # deploy a contract that emits a lifecycle event on calling a specific method as a transaction
        # each account needs its own reference to the contract
        self.log.info('')
        self.log.info('Deploy the storage account through the first user_id connection')
        storage1 = Storage(self, web3_1, 100)
        storage1.deploy(network_connection_1, account_1)
        storage2 = Storage.clone(web3_2, account_2, storage1)
        storage3 = Storage.clone(web3_3, account_3, storage1)
        storage4 = Storage.clone(web3_4, account_4, storage1)

        # make a subscription for all events to the contract, one through each of the connections
        self.log.info('')
        self.log.info('Make a subscription through each of the user_id connections')
        subscriber_1 = AllEventsLogSubscriber(self, network_connection_1, storage1.address, storage1.abi_path,
                                              stdout='subscriber_1.out',
                                              stderr='subscriber_1.err')
        subscriber_1.run()

        subscriber_2 = AllEventsLogSubscriber(self, network_connection_2, storage3.address, storage3.abi_path,
                                              stdout='subscriber_2.out',
                                              stderr='subscriber_2.err')
        subscriber_2.run()

        # each account performs a transaction against the storage contract which results in a lifecycle
        # event being emitted
        self.log.info('')
        self.log.info('Each account performs a transaction through their connection')
        count = 0
        for (name, storage, web3, account, network) in [('web3_1', storage1, web3_1, account_1, network_connection_1),
                                         ('web3_2', storage2, web3_2, account_2, network_connection_1),
                                         ('web3_3', storage3, web3_3, account_3, network_connection_2),
                                         ('web3_4', storage4, web3_4, account_4, network_connection_2)]:
            count = count + 1
            self.log.info('Transacting for %s', name)
            network.transact(self, web3, storage.contract.functions.store(count), account, storage.GAS_LIMIT)

        self.waitForSignal(file='subscriber_1.out', expr='Received event: Stored', condition='==4', timeout=10)
        self.waitForSignal(file='subscriber_2.out', expr='Received event: Stored', condition='==4', timeout=10)

        self.log.info('')
        self.log.info('Perform validation')
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