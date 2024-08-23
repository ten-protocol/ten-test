import os
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 1010

        # the account of the user for the bridges
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')
        self.log.info(accnt1.l1.bus.address)
        self.log.info(accnt1.l1.bridge.address)
        self.log.info(accnt1.l1.network.connection_url(web_socket=True))

        # run the javascript event log subscriber in the background
        stdout = os.path.join(self.output, 'query.out')
        stderr = os.path.join(self.output, 'query.err')
        logout = os.path.join(self.output, 'query.log')
        script = os.path.join(self.input, 'query.js')
        args = []
        args.extend(['--network_ws', accnt1.l1.network.connection_url(web_socket=True)])
        args.extend(['--bus_address', '%s' % accnt1.l1.bus.address])
        args.extend(['--bus_abi', '%s' % accnt1.l1.bus.abi_path])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting task ...', timeout=10)

        # send native from the L1 to the L2
        self.log.info('Send native and wait for the xchain msg on the L2')
        tx_receipt, _, xchain_msg = accnt1.l1.send_native(accnt1.l2.account.address, transfer)
        accnt1.l2.wait_for_message(xchain_msg)

        # we should see the log
        self.assertGrep(file='query.log', expr='Full log')

