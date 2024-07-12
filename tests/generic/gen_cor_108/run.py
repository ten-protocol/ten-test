import os
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage

class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract make some transactions
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'block_notifier.out')
        stderr = os.path.join(self.output, 'block_notifier.err')
        logout = os.path.join(self.output, 'block_notifier.log')
        script = os.path.join(self.input, 'block_notifier.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting task ...', timeout=10)

        network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time))
        network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time))
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time))
        network.transact(self, web3, storage.contract.functions.store(3), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time))

        # wait and validate
        self.waitForGrep(file=logout, expr='Block =', condition='==4', timeout=120)

        network.transact(self, web3, storage.contract.functions.store(4), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time))

        self.assertLineCount(file=logout, expr='Block =', condition='==4')

