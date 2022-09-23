import time
from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.storage import Storage
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    WEBSOCKET = False

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3_1, account1 = network.connect_account1(self, web_socket=self.WEBSOCKET)

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
        num_entries = 0
        num_try = 0
        while True:
            num_try += 1
            entries = event_filter.get_new_entries()
            num_entries += len(entries)
            for event in entries: self.log.info(web3_1.toJSON(event))
            if num_entries == 5 or num_try > 3: break
            time.sleep(0.5)
        self.assertTrue(num_entries == 5)
