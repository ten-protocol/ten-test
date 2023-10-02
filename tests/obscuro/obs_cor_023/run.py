import time
from pysys.constants import TIMEDOUT
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.bridge import BridgeUser
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 1000

        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        l1_balance_before = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance_before = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)

        self.log.info('Send to the message bus to perform a transfer')
        tx_receipt, logs = accnt1.l1.send_to_msg_bus(transfer)
        self.assertTrue(logs[0]['args']['sender'] == props.l1_message_bus_address(self.env))
        self.assertTrue(logs[0]['args']['receiver'] == accnt1.l1.account.address)
        self.assertTrue(logs[0]['args']['amount'] == transfer)

        l1_balance_after = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        start = time.time()
        while True:
            l2_balance_after = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)
            if l2_balance_after > l2_balance_before: break
            if time.time() - start > 10:
                self.addOutcome(TIMEDOUT)
                break

        self.log.info('Account balances;')
        self.log.info('   L1 before: %d', l1_balance_before)
        self.log.info('   L1 after:  %d', l1_balance_after)
        self.log.info('   L1 decr:   %d', (l1_balance_before-l1_balance_after))
        self.log.info('   L2 before: %d', l2_balance_before)
        self.log.info('   L2 after:  %d', l2_balance_after)
        self.log.info('   L2 incr:   %d', (l2_balance_after-l2_balance_before))

        self.assertTrue(l1_balance_before-l1_balance_after > transfer)
        self.assertTrue(l2_balance_after-l2_balance_before == transfer)