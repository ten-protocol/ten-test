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
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contracts
        emitter = EventEmitter(self, web3)
        emitter.deploy(network, account)
        emitter_caller = EventEmitterCaller(self, web3, emitter.address)
        emitter_caller.deploy(network, account)

        # transact ten times and check that both event logs are seen in the tx receipt and have the expected values
        prepend = 'c-'
        for id in range(0,9):
            message = generate_random_string()
            tx_receipt = network.transact(self, web3, emitter_caller.contract.functions.callEmitSimpleEvent(1, prepend, message),
                                          account, emitter_caller.GAS_LIMIT)

            simple_event = emitter.contract.events.SimpleEvent().process_receipt(tx_receipt, errors=DISCARD)[0]
            caller_simple_event = emitter_caller.contract.events.CallerSimpleEvent().process_receipt(tx_receipt, errors=DISCARD)[0]

            self.log.info('  id, message:                %d, %s' % (id, message))
            self.log.info('  simpleEvent.message:        %s' % simple_event['args']['message'])
            self.log.info('  simpleEvent.sender:         %s' % simple_event['args']['sender'])
            self.log.info('  callerSimpleEvent.message:  %s' % caller_simple_event['args']['message'])
            self.log.info('  callerSimpleEvent.sender:   %s' % caller_simple_event['args']['sender'])

            self.assertTrue(len(tx_receipt.logs) == 2, assertMessage='There should be two event logs')
            self.assertTrue(simple_event['args']['message'] == message,
                            assertMessage='SimpleEvent message should be correct')
            self.assertTrue(caller_simple_event['args']['message'] == prepend+message,
                            assertMessage='CallerSimpleEvent message should be correct')

