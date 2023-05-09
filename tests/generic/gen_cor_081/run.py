from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.contracts.storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # deploy the storage and key_storage contracts
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        key_storage = KeyStorage(self, web3)
        key_storage.deploy(network, account)

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            filter_address=storage.address,
            filter_topics=[web3.keccak(text='Stored(uint256)').hex()]
        )
        subscriber.subscribe()

        # perform some transactions on the storage contract
        network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(4), account, storage.GAS_LIMIT)

        # perform some transactions on the key storage contract
        network.transact(self, web3, key_storage.contract.functions.storeItem(100), account, key_storage.GAS_LIMIT)
        network.transact(self, web3, key_storage.contract.functions.setItem('k1', 101), account, key_storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=subscriber.stdout, expr='Stored value = 4', timeout=20)

        self.assertOrderedGrep(file=subscriber.stdout, exprList=['Stored value = %d' % x for x in range(0, 5)])
        self.assertGrep(file=subscriber.stdout, expr='Stored value = 100', contains=False)
        self.assertGrep(file=subscriber.stdout, expr='Stored value = 101', contains=False)
        self.assertLineCount(file=subscriber.stdout, expr='Stored value', condition='== 5')