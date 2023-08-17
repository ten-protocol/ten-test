import os
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import Storage


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
        script = os.path.join(self.input, 'event_listener.py')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--address', '%s' % storage.address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting the polling loop', timeout=10)

        # perform some transactions with a sleep in between
        for i in range(0,5):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Stored value = 4', timeout=20)
        self.assertOrderedGrep(file=stdout, exprList=['Stored value = %d' % x for x in range(0, 5)])
        self.assertLineCount(file=stdout, expr='Stored value', condition='== 5')

