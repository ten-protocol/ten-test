from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy a contract that emits a lifecycle event on calling a specific method as a transaction
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, network)
        subscriber.run(decode_as_stored_event=True)
        subscriber.subscribe()

        # perform some transactions
        network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)

        self.waitForSignal(file='subscriber.out', expr='Stored value = [0-9]', condition='==2', timeout=10)
        self.assertOrderedGrep(file='subscriber.out', exprList=['Stored value = 1', 'Stored value = 2'])
        self.assertLineCount(file='subscriber.out', expr='Stored value = [0-9]', condition='==2')
