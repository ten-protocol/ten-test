import os, json, time
from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.storage import Storage
from ethsys.networks.factory import NetworkFactory
from ethsys.utils.properties import Properties

class PySysTest(EthereumTest):
    WEBSOCKET = False

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        # deploy the contract and dump out the abi
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        abi_path = os.path.join(self.output, 'storage.abi')
        with open(abi_path, 'w') as f: json.dump(storage.abi, f)

        # run a background script to filter and collect events
        self.stdout = os.path.join(self.output, 'listener.out')
        self.stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'event_listener.py')
        args = [network.connection_url(web_socket=False), storage.contract_address, abi_path]
        if self.is_obscuro(): args.extend(['--pk', Properties().account2pk()])
        self.run_python(script, self.stdout, self.stderr, args)
        self.waitForGrep(file=self.stdout, expr='Starting to run the event loop', timeout=10)

        # perform some transactions
        for i in range(0,5):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS)
            time.sleep(1.0)
        self.waitForGrep(file=self.stdout, expr='Stored value', condition='== 5', timeout=20)

    def validate(self):
        exprList=[]
        exprList.append('Stored value = 0')
        exprList.append('Stored value = 1')
        exprList.append('Stored value = 2')
        exprList.append('Stored value = 3')
        exprList.append('Stored value = 4')
        self.assertOrderedGrep(file=self.stdout, exprList=exprList)

