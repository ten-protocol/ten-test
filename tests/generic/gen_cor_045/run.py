import os
from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.storage import Storage
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):
    WEBSOCKET = False

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # run a background python script to pick up events
        script = os.path.join(self.input, 'event_listener.py')
        args = [network.connection_url(web_socket=False), storage.contract_address, storage.abi]
        self.run_python(script, args)

        # perform some transactions
        for i in range(0,5):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS)


