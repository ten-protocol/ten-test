import os
from obscuro.test.basetest import EthereumTest
from obscuro.test.contracts.storage.key_storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        key_storage = KeyStorage(self, web3)
        key_storage.deploy(network, account)

        # run test specific event subscriber
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % network.connection_url(web_socket=True)])
        args.extend(['--filter_address', '%s' % key_storage.contract_address])
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

        # wait and validate
        exprList = []
        exprList.append('Stored value = 101')
        exprList.append('Stored value = 303')
        exprList.append('Stored value = 304')
        exprList.append('Stored value = 106')
        self.waitForGrep(file=stdout, expr='Stored value', condition='== 4', timeout=20)
        self.assertOrderedGrep(file=stdout, exprList=exprList)
