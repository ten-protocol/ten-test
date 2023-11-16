from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage
from ten.test.contracts.storage import KeyStorage
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        key_storage = KeyStorage(self, web3)
        key_storage.deploy(network, account)

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            filter_topics=[web3.keccak(text='Stored(uint256)').hex()],
            decode_as_stored_event=True
        )
        subscriber.subscribe()

        # perform some transactions on the storage contract
        network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(4), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # perform some transactions on the key storage contract
        network.transact(self, web3, key_storage.contract.functions.storeItem(100), account, storage.GAS_LIMIT)
        network.transact(self, web3, key_storage.contract.functions.setItem('k1', 101), account, storage.GAS_LIMIT)

        # wait and validate
        self.waitForGrep(file=subscriber.stdout, expr='Stored value = 4', timeout=20)
        self.waitForGrep(file=subscriber.stdout, expr='Stored value = 100', timeout=20)

        expr_list = []
        expr_list.append('Stored value = 0')
        expr_list.append('Stored value = 1')
        expr_list.append('Stored value = 2')
        expr_list.append('Stored value = 3')
        expr_list.append('Stored value = 4')
        expr_list.append('Stored value = 100')
        self.assertOrderedGrep(file=subscriber.stdout, exprList=expr_list)
        self.assertLineCount(file=subscriber.stdout, expr='Stored value', condition='== 6')

