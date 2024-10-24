from web3.logs import DISCARD
from pysys.constants import FAILED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.emitter import EventEmitter, EventEmitterCaller


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect two accounts to the network
        network_1 = self.get_network_connection(name='user1')
        network_2 = self.get_network_connection(name='user2')
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account2(self)

        # deploy the contracts as account 1, get a reference to the emitter caller for both accounts
        emitter_1 = EventEmitter(self, web3_1)
        emitter_1.deploy(network_1, account_1)
        emitter_1_caller = EventEmitterCaller(self, web3_1, emitter_1.address)
        emitter_1_caller.deploy(network_1, account_1)
        emitter_2_caller = EventEmitterCaller.clone(web3_2, account_2, emitter_1_caller)

        # make a transaction against the caller contract to emit two events as below;
        #   emit CallerAddressEvent with id, msg.sender (account 1 address) - relevant only to account 1
        #   emit AddressEvent       with id, address    (account 2 address) - relevant only to account 2
        tx_receipt_1 = network_1.transact(self, web3_1,
                                          emitter_1_caller.contract.functions.callEmitAddressEvent(1, account_2.address),
                                          account_1, emitter_1_caller.GAS_LIMIT)
        
        event_1 = emitter_1_caller.contract.events.CallerAddressEvent().process_receipt(tx_receipt_1, errors=DISCARD)[0]
        self.log.info('  tx_receipt_1.logs:                   %s' % len(tx_receipt_1['logs']))
        self.log.info('  callerAddressEvent.id:               %s' % event_1['args']['id'])
        self.log.info('  callerAddressEvent.address:          %s' % event_1['args']['_address'])

        try:
            if not self.is_ten():
                tx_receipt_2 = web3_2.eth.get_transaction_receipt(tx_receipt_1.transactionHash)
                event_2 = emitter_2_caller.contract.events.CallerAddressEvent().process_receipt(tx_receipt_2, errors=DISCARD)[0]
                self.log.info('  callerAddressEvent.address:  %s' % event_2['args']['_address'])

        except Exception as e:
            self.log.info('Exception: %s' % e['message'])
            self.addOutcome(FAILED, outcomeReason='We should be able to get the two events from the tx receipt', abortOnError=True)



