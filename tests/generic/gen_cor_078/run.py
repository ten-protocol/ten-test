import os
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties
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
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', ws_url])
        args.extend(['--contract_address', '%s' % storage.contract_address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        if self.is_obscuro(): args.extend(['--pk_to_register', '%s' % Properties().account3pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions
        network.transact(self, web3, storage.contract.functions.setItem('k1', 1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.setItem('k2', 2), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.setItem('k3', 3), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Received event type ItemSet1', condition='>= 3', timeout=10)
        self.waitForGrep(file=stdout, expr='Received event type ItemSet2', condition='>= 3', timeout=10)
        self.waitForGrep(file=stdout, expr='Received event type ItemSet3', condition='>= 3', timeout=10)

        # validate correct count if duplicates are not allowed
        condition = '>=3'
        if not self.ALLOW_EVENT_DUPLICATES: condition = '==3'
        self.assertLineCount(file=stdout, expr='Received event type ItemSet1', condition=condition)
        self.assertLineCount(file=stdout, expr='Received event type ItemSet2', condition=condition)
        self.assertLineCount(file=stdout, expr='Received event type ItemSet3', condition=condition)

