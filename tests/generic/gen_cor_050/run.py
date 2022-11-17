import re
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.error.error import Error
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        error = Error(self, web3, 'foo')
        error.deploy(network, account)

        # force a require
        try:
            self.log.info('Forcing a require on contract function')
            error.contract.functions.force_require().call()
        except Exception as e:
            self.log.info('Exception type: %s' % type(e).__name__)
            self.log.info('Exception args: %s' % e.args[0])
            regex = re.compile('execution reverted:.*Forced require', re.M)
            self.assertTrue(regex.search(e.args[0]) is not None)

        # force a revert
        try:
            self.log.info('Forcing a revert on contract function')
            error.contract.functions.force_revert().call()
        except Exception as e:
            self.log.info('Exception type: %s' % type(e).__name__)
            self.log.info('Exception args: %s' % e.args[0])
            regex = re.compile('execution reverted:.*Forced revert', re.M)
            self.assertTrue(regex.search(e.args[0]) is not None)

        # force assert
        try:
            self.log.info('Forcing an assert on contract function')
            error.contract.functions.force_assert().call()
        except Exception as e:
            self.log.info('Exception type: %s' % type(e).__name__)
            self.log.info('Exception args: %s' % e.args[0])
            regex = re.compile('execution reverted', re.M)
            self.assertTrue(regex.search(e.args[0]) is not None)