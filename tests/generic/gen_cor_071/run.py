import time
from obscuro.test.basetest import EthereumTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3_1, account1 = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3_1, 100)
        storage.deploy(network, account1)

        # create the filter
        event_filter = storage.contract.events.Stored.createFilter(fromBlock='latest')

        # perform some transactions
        for i in range(0, 5):
            network.transact(self, web3_1, storage.contract.functions.store(i), account1, storage.GAS)
            time.sleep(1.0)

        # get the new entries from the filter
        self.log.info('Getting new entries on the Stored event filter')
        values = []
        num_try = 0
        while True:
            num_try += 1
            entries = event_filter.get_new_entries()
            for event in entries:
                values.append(event['args']['value'])
                self.log.info('Stored value = %s' % event['args']['value'])
            if len(values) == 5 or num_try > 3: break
            time.sleep(0.5)
        self.assertTrue(values == [0,1,2,3,4])
