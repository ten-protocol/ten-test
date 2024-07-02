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
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        log_file = os.path.join(self.output, 'poller.log')
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % storage.address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        args.extend(['--log_file', '%s' % log_file])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=log_file, expr='Starting task ...', timeout=10)

        # perform some transactions with a sleep in between
        for i in range(0,5):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=log_file, expr='Stored value = 4', timeout=20)
        self.assertOrderedGrep(file=log_file, exprList=['Stored value = %d' % x for x in range(0, 5)])

        # validate correct count
        self.assertLineCount(file=log_file, expr='Stored value', condition='== 5')
