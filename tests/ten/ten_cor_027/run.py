import os
from ten.test.basetest import TenNetworkTest
from ten.test.utils.bridge import BridgeUser
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        props = Properties()
        transfer = 1010
        transfer_back = 1000

        # the account of the user for the bridges
        accnt1 = BridgeUser(self, props.account1pk(), props.account1pk(), 'accnt1')
        self.log.info(accnt1.l1.bus.address)
        self.log.info(accnt1.l1.bridge.address)
        self.log.info(accnt1.l1.network.connection_url(web_socket=True))

        # run the subscribers
        self.run_client(accnt1.l1, 'l1')
        self.run_client(accnt1.l2, 'l2')

        # send native from the L1 to the L2
        self.log.info('Send native and wait for the xchain msg on the L2')
        _, _, xchain_msg = accnt1.l1.send_native(accnt1.l2.account.address, transfer)
        accnt1.l2.wait_for_message(xchain_msg)

        # send native from the L2 to the L1
        self.log.info('Send native from L2 to L1')
        accnt1.l2.send_native(accnt1.l1.account.address, transfer_back)

        # we should see the logs from both of the value transfer events
        expr_list = []
        expr_list.append('Log transfer sender = %s' % accnt1.l1.bridge.address)
        expr_list.append('Log transfer receiver = %s' % accnt1.l1.account.address)
        expr_list.append('Log transfer amount = %d' % transfer)
        self.assertOrderedGrep(file='query_l1.log', exprList=expr_list)

        expr_list = []
        expr_list.append('Log transfer sender = %s' % accnt1.l2.bridge.address)
        expr_list.append('Log transfer receiver = %s' % accnt1.l1.account.address)
        expr_list.append('Log transfer amount = %d' % transfer_back)
        self.assertOrderedGrep(file='query_l2.log', exprList=expr_list)

    def run_client(self, layer, id):
        # run the javascript event log subscriber in the background
        stdout = os.path.join(self.output, 'query_%s.out'%id)
        stderr = os.path.join(self.output, 'query_%s.err'%id)
        logout = os.path.join(self.output, 'query_%s.log'%id)
        script = os.path.join(self.input, 'query.js')
        args = []
        args.extend(['--network_ws', layer.network.connection_url(web_socket=True)])
        args.extend(['--bus_address', '%s' % layer.bus.address])
        args.extend(['--bus_abi', '%s' % layer.bus.abi_path])
        args.extend(['--sender_address', '%s' % layer.bridge.address])
        args.extend(['--receiver_address', '%s' % layer.account.address])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting task ...', timeout=10)