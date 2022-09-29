import os, json
from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.key_storage import KeyStorage
from ethsys.networks.factory import NetworkFactory
from ethsys.utils.properties import Properties


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3_1, account1 = network.connect_account1(self, web_socket=False)
        web3_2, account2 = network.connect_account2(self, web_socket=False)

        # deploy the contract and dump out the abi
        storage = KeyStorage(self, web3_1)
        storage.deploy(network, account1)
        abi_path = os.path.join(self.output, 'storage.abi')
        with open(abi_path, 'w') as f:
            json.dump(storage.abi, f)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'event_listener.js')
        args = []
        args.extend(['-u', '%s' % network.connection_url(web_socket=False)])
        args.extend(['-w', '%s' % network.connection_url(web_socket=True)])
        args.extend(['-a', '%s' % storage.contract_address])
        args.extend(['-b', '%s' % abi_path])
        args.extend(['-p', '%s' % Properties().account3pk()])
        args.extend(['-f', '%s' % account2.address])
        if self.is_obscuro(): args.append('--obscuro')
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions
        contract_1 = storage.contract
        contract_2 = web3_2.eth.contract(address=storage.contract_address, abi=storage.abi)
        network.transact(self, web3_1, contract_1.functions.setItem('account1', 1), account1, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('foo', 2), account1, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('bar', 3), account1, storage.GAS)
        network.transact(self, web3_2, contract_2.functions.setItem('account2', 2), account2, storage.GAS)

        # wait and validate
        self.waitForGrep(file=stdout, expr='ItemSet1:', condition='== 1', timeout=10)
        self.assertGrep(file=stdout, expr='ItemSet1: account1 1', contains=False)
        self.assertGrep(file=stdout, expr='ItemSet1: account2 2')


