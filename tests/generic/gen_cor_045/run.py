import os, json
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

        # dump out the abi
        abi_path = os.path.join(self.output, 'storage.abi')
        with open(abi_path, 'w') as f: json.dump(storage.abi, f)

        # run a background python script to pick up events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'event_listener.py')
        args = [network.connection_url(web_socket=False), storage.contract_address, abi_path]
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting to run the event loop', timeout=10)

        # perform some transactions
        for i in range(0,5):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS)

        self.waitForGrep(file=stdout, expr='args.*value', condition='== 5', timeout=20)


