import string, random
from web3.logs import DISCARD
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.emitter import EventEmitter, EventEmitterCaller


def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect two accounts to the network
        network_1 = self.get_network_connection(name='user1')
        network_2 = self.get_network_connection(name='user2')
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account2(self)

        # deploy the contracts as account 1, get a reference for both accounts
        emitter_1 = EventEmitter(self, web3_1)
        emitter_1.deploy(network_1, account_1)
        emitter_1_caller = EventEmitterCaller(self, web3_1, emitter_1.address)
        emitter_1_caller.deploy(network_1, account_1)
        emitter_2 = EventEmitter.clone(web3_2, account_2, emitter_1)

        # transact and check event logs in the tx receipt
        #   SimpleEvent(id, message, msg.sender) - emitted where msg.sender is the CallerSimpleEvent address
        #   CallerSimpleEvent(id, prepend+message, msg.sender) - where msg.sender is account 1

        # check for account 1
        id = 1
        prepend = 'c-'
        message = generate_random_string()

        self.log.info('Submitting tx to the EventEmitter contract directly')
        tx_receipt_0 = network_1.transact(self, web3_1,
                                          emitter_1.contract.functions.emitSimpleEvent(id, message),
                                          account_1, emitter_1.GAS_LIMIT)

        self.log.info('Submitting tx to the EventEmitterCaller contract (which then calls EventEmitter')
        tx_receipt_1 = network_1.transact(self, web3_1,
                                          emitter_1_caller.contract.functions.callEmitSimpleEvent(id, prepend, message),
                                          account_1, emitter_1_caller.GAS_LIMIT)
        simple_event_1 = emitter_1.contract.events.SimpleEvent().process_receipt(tx_receipt_1, errors=DISCARD)[0]
        caller_simple_event_1 = emitter_1_caller.contract.events.CallerSimpleEvent().process_receipt(tx_receipt_1, errors=DISCARD)[0]

        self.log.info('  id, message:                %d, %s' % (id, message))
        self.log.info('  account1.address            %s' % account_1.address)
        self.log.info('  account2.address            %s' % account_2.address)
        self.log.info('  simpleEvent.message:        %s' % simple_event_1['args']['message'])
        self.log.info('  simpleEvent.sender:         %s' % simple_event_1['args']['sender'])
        self.log.info('  callerSimpleEvent.message:  %s' % caller_simple_event_1['args']['message'])
        self.log.info('  callerSimpleEvent.sender:   %s' % caller_simple_event_1['args']['sender'])

        self.assertTrue(len(tx_receipt_1.logs) == 2, assertMessage='There should be two event logs')
        self.assertTrue(simple_event_1['args']['message'] == message, assertMessage='SimpleEvent message incorrect')
        self.assertTrue(caller_simple_event_1['args']['message'] == prepend+message, assertMessage='CallerSimpleEvent message incorrect')

        # check for account 2
        self.log.info('Attempting to get tx receipt for account 2')
        tx_receipt_2 = web3_2.eth.get_transaction_receipt(tx_receipt_1.transactionHash)
        simple_event_2 = emitter_2.contract.events.SimpleEvent().process_receipt(tx_receipt_2, errors=DISCARD)[0]
        self.log.info('  id, message:                %d, %s' % (id, message))
        self.log.info('  account1.address            %s' % account_1.address)
        self.log.info('  account2.address            %s' % account_2.address)
        self.log.info('  simpleEvent.message:        %s' % simple_event_2['args']['message'])
        self.log.info('  simpleEvent.sender:         %s' % simple_event_2['args']['sender'])

        self.assertTrue(len(tx_receipt_2.logs) == 1, assertMessage='There should be one event logs')
        self.assertTrue(simple_event_2['args']['message'] == message, assertMessage='SimpleEvent message incorrect')