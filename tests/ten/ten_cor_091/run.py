import re
from web3.logs import DISCARD
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.emitter import EventEmitter, EventEmitterCaller


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect two accounts to the network
        network_1 = self.get_network_connection(name='user1')
        network_2 = self.get_network_connection(name='user2')
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account2(self)

        # deploy the contracts as account 1
        emitter_1 = EventEmitter(self, web3_1)
        emitter_1.deploy(network_1, account_1)
        emitter_1_caller = EventEmitterCaller(self, web3_1, emitter_1.address)
        emitter_1_caller.deploy(network_1, account_1)

        # transact and check event logs in the tx receipt
        # events emitted will be
        #   AddressEvent(id, _address) - emitted where _address is account 1 address
        #   CallerAddressEvent(id, _address) - emitted where _address is msg.sender as account 1 address

        # check for account 1
        id = 1
        self.log.info('Submitting tx and get tx receipt for account 1')
        tx_receipt_1 = network_1.transact(self, web3_1,
                                          emitter_1_caller.contract.functions.callEmitAddressEvent(id, account_1.address),
                                          account_1, emitter_1_caller.GAS_LIMIT)

        simple_event_1 = emitter_1.contract.events.AddressEvent().process_receipt(tx_receipt_1, errors=DISCARD)[0]
        caller_simple_event_1 = emitter_1_caller.contract.events.CallerAddressEvent().process_receipt(tx_receipt_1, errors=DISCARD)[0]

        self.log.info('  id:                          %d' % id)
        self.log.info('  account1.address             %s' % account_1.address)
        self.log.info('  account2.address             %s' % account_2.address)
        self.log.info('  addressEvent._address:       %s' % simple_event_1['args']['_address'])
        self.log.info('  callerAddressEvent._address: %s' % caller_simple_event_1['args']['_address'])

        self.assertTrue(len(tx_receipt_1.logs) == 2, assertMessage='There should be two event logs')

        # check for account 2
        try:
            self.log.info('Attempting to get tx receipt for account 2')
            web3_2.eth.get_transaction_receipt(tx_receipt_1.transactionHash)
        except Exception as e:
            self.log.info('Exception type: %s', type(e).__name__)
            self.log.info('Exception args: %s', e.args)
            regex = re.compile('not authorised', re.M)
            self.assertTrue(regex.search(e.args[0]['message']) is not None)