import os
from obscuro.test.obscuro_test import ObscuroTest
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.ws_proxy import WebServerProxy


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3_1, account1 = network.connect_account1(self)
        web3_2, account2 = network.connect_account2(self)

        # deploy the contract and dump out the abi
        storage = KeyStorage(self, web3_1)
        storage.deploy(network, account1)

        # go through a proxy to log websocket communications if needed
        ws_url = network.connection_url(web_socket=True)
        if self.PROXY: ws_url = WebServerProxy.create(self).run(ws_url, 'proxy.logs')

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', ws_url])
        args.extend(['--contract_address', '%s' % storage.contract_address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        args.extend(['--filter_address', '%s' % account2.address])
        args.extend(['--filter_key', '%s' % 'r1'])
        if self.is_obscuro():
            self.log.info('Adding private key to register')
            args.extend(['--pk_to_register', '%s' % Properties().account3pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Started tasks', timeout=10)

        # perform some transactions
        contract_1 = storage.contract
        contract_2 = web3_2.eth.contract(address=storage.contract_address, abi=storage.abi)
        network.transact(self, web3_1, contract_1.functions.setItem('k1', 1), account1, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('foo', 2), account1, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('bar', 3), account1, storage.GAS)
        network.transact(self, web3_2, contract_2.functions.setItem('k2', 2), account2, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('r1', 10), account1, storage.GAS)
        network.transact(self, web3_1, contract_1.functions.setItem('r2', 11), account1, storage.GAS)

        # wait and validate - ItemSet1 filter on sender is account2.address
        #  event ItemSet1(string key, uint256 value, address indexed setter);
        self.waitForGrep(file=stdout, expr='Task1:', condition='== 1', timeout=10)
        self.assertGrep(file=stdout, expr='Task1: k1 1', contains=False)
        self.assertGrep(file=stdout, expr='Task1: k2 2')

        # wait and validate - ItemSet2 filter on value 2 or 3
        #  event ItemSet2(string key, uint256 indexed value, address indexed setter);
        self.waitForGrep(file=stdout, expr='Task2:', condition='== 3', timeout=10)
        self.assertOrderedGrep(file=stdout, exprList=['Task2: foo 2', 'Task2: bar 3', 'Task2: k2 2'])

        # wait and validate - filter on key is r1
        #  event ItemSet3(string indexed key, uint256 value, address setter);
        self.waitForGrep(file=stdout, expr='Task3:', condition='== 1', timeout=10)
        self.assertGrep(file=stdout, expr='Task3: 10')

