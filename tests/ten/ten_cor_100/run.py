from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account2(self)

        self.log.info('Activate when no session key')
        active = self.activate_session_key(network.connection_url())
        self.log.info('  Session active: %s' % active)
        self.assertTrue(active == None)

        self.log.info('De-activate when no session key')
        active = self.deactivate_session_key(network.connection_url())
        self.log.info('  Session active: %s' % active)
        self.assertTrue(active == None)

        self.log.info('Activate when have session key')
        sk = self.get_session_key(network.connection_url())
        active = self.activate_session_key(network.connection_url())
        self.log.info('  Session key: %s' % sk)
        self.log.info('  Session active: %s' % active)
        self.assertTrue(active == 1)

        self.log.info('De-activate when have session key')
        deactive = self.deactivate_session_key(network.connection_url())
        self.log.info('  Session active: %s' % deactive)
        self.assertTrue(active == 1)