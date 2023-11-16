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
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % storage.address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
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

        # validate correct count
        condition = '==3'
        self.assertLineCount(file=stdout, expr='Received event type ItemSet1', condition=condition)
        self.assertLineCount(file=stdout, expr='Received event type ItemSet2', condition=condition)
        self.assertLineCount(file=stdout, expr='Received event type ItemSet3', condition=condition)

