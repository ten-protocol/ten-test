import os
from obscuro.test.basetest import ObscuroTest
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.ws_proxy import WebServerProxy


class PySysTest(ObscuroTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        key_storage = KeyStorage(self, web3)
        key_storage.deploy(network, account)

        # go through a proxy to log websocket communications if needed
        ws_url = network.connection_url(web_socket=True)
        if self.PROXY: ws_url = WebServerProxy.create(self).run(ws_url, 'proxy.logs')

        # run test specific event subscriber
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', ws_url])
        args.extend(['--filter_key1', 'k1'])
        args.extend(['--filter_key2', 'k3'])
        if self.is_obscuro(): args.extend(['--pk_to_register', '%s' % Properties().account3pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions on the key storage contract
        network.transact(self, web3, key_storage.contract.functions.setItem('k1', 101), account, key_storage.GAS)
        network.transact(self, web3, key_storage.contract.functions.setItem('k2', 202), account, key_storage.GAS)
        network.transact(self, web3, key_storage.contract.functions.setItem('k3', 303), account, key_storage.GAS)
        network.transact(self, web3, key_storage.contract.functions.setItem('k3', 304), account, key_storage.GAS)
        network.transact(self, web3, key_storage.contract.functions.setItem('k2', 205), account, key_storage.GAS)
        network.transact(self, web3, key_storage.contract.functions.setItem('k1', 106), account, key_storage.GAS)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Stored value = [0-9]{3}$', condition='== 4', timeout=20)

        expr_list = ['Stored value = 101', 'Stored value = 303', 'Stored value = 304', 'Stored value = 106']
        self.assertOrderedGrep(file=stdout, exprList=expr_list)
