import os
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import KeyStorage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        key_storage = KeyStorage(self, web3)
        key_storage.deploy(network, account)

        # run test specific event subscriber
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        logout = os.path.join(self.output, 'subscriber.log')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--filter_key1', 'k1'])
        args.extend(['--filter_key2', 'k3'])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Subscribed for event logs', timeout=10)

        # perform some transactions on the key storage contract
        network.transact(self, web3, key_storage.contract.functions.setItem('k1', 101), account, key_storage.GAS_LIMIT)
        network.transact(self, web3, key_storage.contract.functions.setItem('k2', 202), account, key_storage.GAS_LIMIT)
        network.transact(self, web3, key_storage.contract.functions.setItem('k3', 303), account, key_storage.GAS_LIMIT)
        network.transact(self, web3, key_storage.contract.functions.setItem('k3', 304), account, key_storage.GAS_LIMIT)
        network.transact(self, web3, key_storage.contract.functions.setItem('k2', 205), account, key_storage.GAS_LIMIT)
        network.transact(self, web3, key_storage.contract.functions.setItem('k1', 106), account, key_storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=logout, expr='Stored value = 106', timeout=20)

        expr_list = ['Stored value = 101', 'Stored value = 303', 'Stored value = 304', 'Stored value = 106']
        self.assertOrderedGrep(file=logout, exprList=expr_list)
        self.assertLineCount(file=logout, expr='Stored value', condition='== 4')

