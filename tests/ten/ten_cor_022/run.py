from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 1000

        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        l1_balance_before = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance_before = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)

        # subscribe for the deposit event
        subscriber = FilterLogSubscriber(self, accnt1.l2.network)
        filter_address = '0'*24 + accnt1.l2.account.address.lower().strip().replace('0x', '')
        subscriber.run(
            filter_topics=[accnt1.l2.web3.keccak(text='NativeDeposit(address,uint256)').hex(), '0x'+filter_address]
        )
        subscriber.subscribe()

        # send native from the L1 to the L2, wait for the deposit event amount to be seen
        self.log.info('Send native and wait for the deposit event on the L2')
        tx_receipt, _ = accnt1.l1.send_native(accnt1.l2.account.address, transfer)
        self.waitForGrep('subscriber.out', expr='data:.*03e8', timeout=20)

        l1_balance_after = accnt1.l1.web3.eth.get_balance(accnt1.l1.account.address)
        l2_balance_after = accnt1.l2.web3.eth.get_balance(accnt1.l2.account.address)

        self.log.info('Account balances;')
        self.log.info('   L1 before: %d', l1_balance_before)
        self.log.info('   L1 after:  %d', l1_balance_after)
        self.log.info('   L1 decr:   %d', (l1_balance_before-l1_balance_after))
        self.log.info('   L2 before: %d', l2_balance_before)
        self.log.info('   L2 after:  %d', l2_balance_after)
        self.log.info('   L2 incr:   %d', (l2_balance_after-l2_balance_before))

        self.assertTrue(l1_balance_before-l1_balance_after > transfer)
        self.assertTrue(l2_balance_after-l2_balance_before == transfer)