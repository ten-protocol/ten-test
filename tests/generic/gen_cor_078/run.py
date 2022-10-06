import os, json
from obscuro.test.basetest import EthereumTest
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the contract and dump out the abi
        storage = KeyStorage(self, web3)
        storage.deploy(network, account)
        abi_path = os.path.join(self.output, 'storage.abi')
        with open(abi_path, 'w') as f:
            json.dump(storage.abi, f)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'event_listener.js')
        args = []
        args.extend(['--url_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--url_ws', '%s' % network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % storage.contract_address])
        args.extend(['--abi', '%s' % abi_path])
        args.extend(['--pk', '%s' % Properties().account3pk()])
        if self.is_obscuro(): args.append('--obscuro')
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions
        network.transact(self, web3, storage.contract.functions.setItem('k1', 1), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.setItem('k2', 2), account, storage.GAS)
        network.transact(self, web3, storage.contract.functions.setItem('k3', 3), account, storage.GAS)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Received event type', condition='== 9', timeout=10)
        self.assertLineCount(file=stdout, expr='Received event type ItemSet1', condition='==3')
        self.assertLineCount(file=stdout, expr='Received event type ItemSet2', condition='==3')
        self.assertLineCount(file=stdout, expr='Received event type ItemSet3', condition='==3')

