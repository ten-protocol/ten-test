from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the storage contract
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        # run a javascript subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            decode_as_stored_event=True,
            filter_address=storage.address,
            filter_topics=[web3.keccak(text='Stored(uint256)').hex()]
        )

        # perform some transactions on the storage contract
        network.transact(self, web3, storage.contract.functions.store(100), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(101), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 2.0)

        # subscribe and transact
        subscriber.subscribe()
        network.transact(self, web3, storage.contract.functions.store(102), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(103), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 2.0)

        # unsubscribe and transact
        subscriber.unsubscribe()
        network.transact(self, web3, storage.contract.functions.store(104), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(105), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 2.0)

        # wait and validate
        self.waitForGrep(file=subscriber.stdout, expr='Stored value = [0-9]{3}$', condition='== 2', timeout=20)
        self.assertOrderedGrep(file=subscriber.stdout, exprList=['Stored value = 102', 'Stored value = 103'])

