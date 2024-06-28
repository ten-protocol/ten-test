import os
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.emitter import EventEmitter


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network on the primary gateway and deploy contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        emitter = EventEmitter(self, web3, 100)
        emitter.deploy(network, account)

        # make some transactions
        network.transact(self, web3, emitter.contract.functions.emitSimpleEvent(1, 'one'), account, emitter.GAS_LIMIT)
        network.transact(self, web3, emitter.contract.functions.emitSimpleEvent(2, 'two'), account, emitter.GAS_LIMIT)
        network.transact(self, web3, emitter.contract.functions.emitSimpleEvent(3, 'three'), account, emitter.GAS_LIMIT)
        network.transact(self, web3, emitter.contract.functions.emitSimpleEvent(1, 'four'), account, emitter.GAS_LIMIT)
        network.transact(self, web3, emitter.contract.functions.emitSimpleEvent(2, 'five'), account, emitter.GAS_LIMIT)
        network.transact(self, web3, emitter.contract.functions.emitSimpleEvent(3, 'six'), account, emitter.GAS_LIMIT)

        # poll for the events
        self.run_poller_simple(network, emitter, 1)

        # validate
        expr = ['Event: id= 1 message= one', 'Event: id= 1 message= four']
        self.assertOrderedGrep('poller_simple.out', exprList=expr)
        self.assertGrep('poller_simple.out', expr='Event: id= 2', contains=False)
        self.assertGrep('poller_simple.out', expr='Event: id= 3', contains=False)

    def run_poller_simple(self, network, emitter, id_filter):
        stdout = os.path.join(self.output, 'poller_simple.out')
        stderr = os.path.join(self.output, 'poller_simple.err')
        script = os.path.join(self.input, 'poller_simple.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', '%s' % emitter.address])
        args.extend(['--contract_abi', '%s' % emitter.abi_path])
        args.extend(['--id_filter', '%d' % id_filter])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Poller completed', timeout=10)
