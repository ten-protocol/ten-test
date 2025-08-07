import re
from pysys.constants import FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway and deploy the storage contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # get a session key
        sk = self.get_session_key(network.connection_url())
        self.log.info('Session key is %s', sk)
        lsk = self.list_session_key(network.connection_url())
        self.log.info('Listed session key is %s', lsk)
        self.assertTrue(sk == lsk, assertMessage='Should match with the original session key')

        # activate the session key
        self.activate_session_key(network.connection_url())
        lsk = self.list_session_key(network.connection_url())
        self.log.info('Listed session key is %s', lsk)
        self.assertTrue(sk == lsk, assertMessage='Should match with the original session key')

        # deactivate the session key
        self.deactivate_session_key(network.connection_url())
        lsk = self.list_session_key(network.connection_url())
        self.log.info('Listed session key is %s', lsk)
        self.assertTrue(sk == lsk, assertMessage='Should match with the original session key')

        # delete the session key
        self.delete_session_key(network.connection_url())
        lsk = self.list_session_key(network.connection_url())
        self.log.info('Listed session key is %s', lsk)
        self.assertTrue('0x' == lsk, assertMessage='Should be no key')


