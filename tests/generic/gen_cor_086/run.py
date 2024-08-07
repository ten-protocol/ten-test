import os
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import KeyStorage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = KeyStorage(self, web3)
        storage.deploy(network, account)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        logout = os.path.join(self.output, 'listener.log')
        script = os.path.join(self.input, 'listener.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % storage.address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        args.extend(['--filter_value', '2'])
        args.extend(['--filter_key', 'k2'])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting task ...', timeout=10)

        # perform some transactions with a sleep in between
        network.transact(self, web3, storage.contract.functions.setItem('k1', 1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.setItem('foo', 2), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.setItem('bar', 3), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.setItem('k2', 4), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.setItem('r1', 5), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.setItem('r2', 2), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=logout, expr='ItemSet1, key = k2 stored value = 4', timeout=20)
        self.waitForGrep(file=logout, expr='ItemSet2, key = r2 stored value = 2', timeout=20)

        # contract.filters.ItemSet1(options.filter_key, null) - key is k2
        expr_list = ['ItemSet1, key = k2 stored value = 4']
        self.assertOrderedGrep(file=logout, exprList=expr_list)

        # contract.filters.ItemSet2(null, options.filter_value) - value is 2
        expr_list = ['ItemSet2, key = foo stored value = 2', 'ItemSet2, key = r2 stored value = 2']
        self.assertOrderedGrep(file=logout, exprList=expr_list)
        self.assertLineCount(file=logout, expr='ItemSet1', condition='== 1')
        self.assertLineCount(file=logout, expr='ItemSet2', condition='== 2')
