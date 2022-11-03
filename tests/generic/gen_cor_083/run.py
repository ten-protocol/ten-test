from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.helpers.log_subscriber import FilterLogSubscriber
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the storage contract
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        # run a javascript subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(
            pk_to_register=Properties().account3pk(),
            filter_address=storage.contract_address,
            filter_topics=[web3.keccak(text='Stored(uint256)').hex()]
        )

        # perform some transactions on the storage contract
        network.transact(self, web3, storage.contract.functions.store(100), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(101), account, storage.GAS)
        self.wait(float(self.block_time) * 1.1)

        # subscribe and transact
        subscriber.subscribe()
        network.transact(self, web3, storage.contract.functions.store(102), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(103), account, storage.GAS)
        self.wait(float(self.block_time) * 1.1)

        # unsubscribe and transact
        subscriber.unsubscribe()
        network.transact(self, web3, storage.contract.functions.store(104), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(105), account, storage.GAS)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=subscriber.stdout, expr='Stored value = [0-9]{3}$', condition='== 2', timeout=20)
        self.assertOrderedGrep(file=subscriber.stdout, exprList=['Stored value = 102', 'Stored value = 103'])

