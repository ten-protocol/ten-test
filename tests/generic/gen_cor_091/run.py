import os
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.emitter import EventEmitter


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network on the primary gateway and deploy contract
        network = self.get_network_connection()
        web3_1, account_1 = network.connect_account1(self)
        web3_2, account_2 = network.connect_account2(self)

        emitter = EventEmitter(self, web3_1, 100)
        emitter.deploy(network, account_1)

        # start the subscriber and poller
        self.run_poller(network, emitter, id_filter=1)
        self.run_subscriber(network, emitter, id_filter=1)

        # make some transactions
        network.transact(self, web3_2, emitter.contract.functions.emitSimpleEvent(1, 'one'), account_2, emitter.GAS_LIMIT)
        network.transact(self, web3_2, emitter.contract.functions.emitSimpleEvent(1, 'two'), account_2, emitter.GAS_LIMIT)
        network.transact(self, web3_2, emitter.contract.functions.emitSimpleEvent(1, 'three'), account_2, emitter.GAS_LIMIT)
        network.transact(self, web3_2, emitter.contract.functions.emitSimpleEvent(1, 'four'), account_2, emitter.GAS_LIMIT)
        network.transact(self, web3_2, emitter.contract.functions.emitSimpleEvent(1, 'five'), account_2, emitter.GAS_LIMIT)
        network.transact(self, web3_2, emitter.contract.functions.emitSimpleEvent(1, 'six'), account_2, emitter.GAS_LIMIT)

        # wait for the poller to have made 6 attempts
        self.waitForSignal(os.path.join(self.output, 'poller.log'), expr='Getting past SimpleEvent events', condition=">=6")
        self.assertGrep(os.path.join(self.output, 'poller.log'), expr='Events received = 6')
        self.assertLineCount(os.path.join(self.output, 'subscriber.log'), expr='Filtered SimpleEvent', condition='==6')

    def run_subscriber(self, network, emitter, id_filter):
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        logout = os.path.join(self.output, 'subscriber.log')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', '%s' % emitter.address])
        args.extend(['--contract_abi', '%s' % emitter.abi_path])
        args.extend(['--id_filter', str(id_filter)])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Listening for filtered events...', timeout=10)

    def run_poller(self, network, emitter, id_filter):
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        logout = os.path.join(self.output, 'poller.log')
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', '%s' % emitter.address])
        args.extend(['--contract_abi', '%s' % emitter.abi_path])
        args.extend(['--id_filter', str(id_filter)])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
