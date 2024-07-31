from web3.logs import DISCARD
from pysys.constants import FAILED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.emitter import EventEmitter, EventEmitterCaller


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network_1 = self.get_network_connection(name='user1')
        network_2 = self.get_network_connection(name='user2')
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account2(self)

        # deploy the contracts
        emitter = EventEmitter(self, web3_1)
        emitter.deploy(network_1, account_1)
        emitter_caller = EventEmitterCaller(self, web3_1, emitter.address)
        emitter_caller.deploy(network_1, account_1)

        # transact in a loop
        for id in range(0, 9):
            # callEmitAddressEvent will emit the CallerAddressEvent with the msg.sender address in it, and through the
            # contract call will also emit AddressEvent with the address field supplied
            tx_receipt_1 = network_1.transact(self, web3_1,
                                          emitter_caller.contract.functions.callEmitAddressEvent(1, account_2.address),
                                          account_1, emitter_caller.GAS_LIMIT)
            self.log.info(tx_receipt_1.logs)
            tx_receipt_2 = web3_2.eth.get_transaction_receipt(tx_receipt_1.transactionHash)

            try:
                event_1 = emitter_caller.contract.events.CallerAddressEvent().process_receipt(tx_receipt_1, errors=DISCARD)[0]
                event_2 = emitter_caller.contract.events.CallerAddressEvent().process_receipt(tx_receipt_2, errors=DISCARD)[0]


                self.log.info('  simpleEvent.address:        %s' % event_1['args']['_address'])
                self.log.info('  callerSimpleEvent.address:  %s' % event_2['args']['_address'])
            except:
                self.addOutcome(FAILED, outcomeReason='We should be able to get the two events from the tx receipt', abortOnError=True)



