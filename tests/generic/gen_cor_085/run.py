import os
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 100)
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
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting task ...', timeout=10)

        # perform some transactions with a sleep in between
        network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(4), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=logout, expr='Stored value = 4', timeout=20)
        self.assertOrderedGrep(file=logout, exprList=['Stored value = %d' % x for x in range(0, 5)])
        self.assertLineCount(file=logout, expr='Stored value', condition='== 5')