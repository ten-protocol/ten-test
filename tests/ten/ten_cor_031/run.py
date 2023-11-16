import os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy a contract that emits a lifecycle event on calling a specific method as a transaction
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # create two connections, each with their own user id (via a join call)
        network_shared = self.get_network_connection(name='shared')
        network_shared.connect_account2(self)
        network_shared.connect_account3(self)

        # make a subscription for all event logs, one through each of the connections
        self.subscribe(network_shared)

        # perform some transactions
        network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS_LIMIT)
        network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS_LIMIT)

        self.waitForSignal(file='subscriber.out', expr='Stored value = [0-9]', condition='==2', timeout=10)
        self.assertOrderedGrep(file='subscriber.out', exprList=['Stored value = 1', 'Stored value = 2'])
        self.assertLineCount(file='subscriber.out', expr='Stored value = [0-9]', condition='==2')

    def subscribe(self, network):
        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscribed for event logs', timeout=10)