import os
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.helpers.ws_proxy import WebServerProxy


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = KeyStorage(self, web3)
        storage.deploy(network, account)

        # go through a proxy to log websocket communications if needed
        ws_url = network.connection_url(web_socket=True)
        if self.PROXY: ws_url = WebServerProxy.create(self).run(ws_url, 'proxy.logs')

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_ws', ws_url])
        args.extend(['--address', '%s' % storage.address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        args.extend(['--filter_key', '%s' % 'r1'])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Started tasks', timeout=10)

        # perform some transactions
        network.transact(self, web3, storage.contract.functions.setItem('k1', 1), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)
        network.transact(self, web3, storage.contract.functions.setItem('foo', 2), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)
        network.transact(self, web3, storage.contract.functions.setItem('bar', 3), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)
        network.transact(self, web3, storage.contract.functions.setItem('k2', 2), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)
        network.transact(self, web3, storage.contract.functions.setItem('r1', 10), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)
        network.transact(self, web3, storage.contract.functions.setItem('r2', 11), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate - filter on key is r1
        # event ItemSet1(string indexed key, uint256 value)
        self.waitForGrep(file=stdout, expr='Task1:', timeout=10)
        self.assertGrep(file=stdout, expr='Task1: 10')

        # wait and validate - ItemSet2 filter on value 2 or 3
        # event ItemSet2(string key, uint256 indexed value)
        self.waitForGrep(file=stdout, expr='Task2: k2 2', timeout=10)
        self.assertOrderedGrep(file=stdout, exprList=['Task2: foo 2', 'Task2: bar 3', 'Task2: k2 2'])

        # validate correct count
        self.assertLineCount(file=stdout, expr='Task2', condition='== 3')


