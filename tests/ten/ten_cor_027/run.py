from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties
from ten.test.helpers.log_subscriber import FilterLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 1000

        # the account of the user for the bridges
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')

        # run the javascript event log subscriber in the background
        subscriber = FilterLogSubscriber(self, accnt1.l1.network)
        subscriber.run(
            decode_as_stored_event=False,
            filter_address=accnt1.l1.bus.address,
            filter_topics=[accnt1.l1.web3.keccak(text='ValueTransfer(address,address,uint256,uint64)').hex()]
        )
        subscriber.subscribe()

        # send native from the L1 to the L2
        self.log.info('Send native and wait for the xchain msg on the L2')
        tx_receipt, _, xchain_msg = accnt1.l1.send_native(accnt1.l2.account.address, transfer)
        accnt1.l2.wait_for_message(xchain_msg)

        # we should see the log
        self.assertGrep(file='subscriber.out', expr='Full log')

