from web3.logs import DISCARD
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.emitter import EventEmitter, EventEmitterCaller


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect two accounts to the network
        network = self.get_network_connection(name='user1')
        web3, account = network.connect_account1(self)

        # deploy the contracts as account 1, get a reference for both accounts
        emitter = EventEmitter(self, web3)
        emitter.deploy(network, account)
        emitter_caller = EventEmitterCaller(self, web3, emitter.address)
        emitter_caller.deploy(network, account)

        # submit a tx to EventEmitter.emitSimpleEvent to emit a SimpleEvent, and then for
        # EventEmitterCaller.callEmitSimpleEvent to emit a SimpleEvent (as a call into
        # EventEmitter.emitSimpleEvent) and a CallerSimpleEvent directly
        self.log.info('Submitting tx to the EventEmitter contract directly')
        tx_receipt_0 = network.transact(self, web3,
                                        emitter.contract.functions.emitSimpleEvent(1, 'a msg'),
                                        account, emitter.GAS_LIMIT)

        self.log.info('Submitting tx to the EventEmitterCaller contract (which then calls EventEmitter')
        tx_receipt_1 = network.transact(self, web3,
                                        emitter_caller.contract.functions.callEmitSimpleEvent(2, 'c-', 'another msg'),
                                        account, emitter_caller.GAS_LIMIT)

        # there should be two event logs, and we should be able to extract them both
        self.assertTrue(len(tx_receipt_1.logs) == 2, assertMessage='There should be two event logs')
        simple_event = emitter.contract.events.SimpleEvent().process_receipt(tx_receipt_1, errors=DISCARD)[0]
        caller_simple_event = emitter_caller.contract.events.CallerSimpleEvent().process_receipt(tx_receipt_1, errors=DISCARD)[0]
        self.assertTrue(simple_event['args']['message'] == 'another msg')
        self.assertTrue(caller_simple_event['args']['message'] == 'c-another msg')

