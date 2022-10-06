import os, time
from obscuro.test.basetest import EthereumTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        key_storage = KeyStorage(self, web3)
        key_storage.deploy(network, account)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'event_listener.js')
        args = []
        args.extend(['--url_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--url_ws', '%s' % network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % storage.contract_address])
        args.extend(['--pk', '%s' % Properties().account3pk()])
        if self.is_obscuro(): args.append('--obscuro')
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions on the storage contract
        for i in range(0, 5):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS)
            time.sleep(1.0)

        # perform some transactions on the key storage contract
        network.transact(self, web3, key_storage.contract.functions.storeItem(100), account, key_storage.GAS)
        network.transact(self, web3, key_storage.contract.functions.setItem('k1', 101), account, key_storage.GAS)

        # wait and validate
        exprList = []
        exprList.append('Stored value = 0')
        exprList.append('Stored value = 1')
        exprList.append('Stored value = 2')
        exprList.append('Stored value = 3')
        exprList.append('Stored value = 4')
        self.waitForGrep(file=stdout, expr='Stored value', condition='== 5', timeout=20)
        self.assertOrderedGrep(file=stdout, exprList=exprList)
        self.assertGrep(file=stdout, expr='Stored value = 100', contains=False)
