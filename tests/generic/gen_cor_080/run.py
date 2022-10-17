from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.helpers.log_subscriber import EventLogSubscriber
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the contract, dump out the abi, make some transactions
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS)
        tx = network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS)

        # run the javascript event log subscriber in the background
        subscriber = EventLogSubscriber(self, network)
        subscriber.run(
            pk_to_register=Properties().account3pk(),
            filter_from_block=tx.blockNumber,
            filter_topics=[web3.keccak(text='Stored(uint256)').hex()],
            proxy=self.PROXY
        )
        subscriber.subscribe()

        # perform some more transactions
        network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(4), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.store(5), account, storage.GAS)

        # wait and validate
        self.waitForGrep(file=subscriber.stdout, expr='Stored value = [0-9]$', condition='== 5', timeout=20)
        self.assertOrderedGrep(file=subscriber.stdout, exprList=['Stored value = %d' % x for x in range(1, 6)])
