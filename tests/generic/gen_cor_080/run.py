from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract make some transactions
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        tx = network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 2)

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            filter_from_block=tx.blockNumber,
            filter_topics=[web3.keccak(text='Stored(uint256)').hex()]
        )
        subscriber.subscribe()

        # perform some more transactions
        network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(4), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(5), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 2)

        # wait and validate
        self.waitForGrep(file=subscriber.stdout, expr='Stored value = 5', timeout=20)
        self.assertOrderedGrep(file=subscriber.stdout, exprList=['Stored value = %d' % x for x in range(1, 6)])
