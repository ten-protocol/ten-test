import re
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.error import Error


class PySysTest(GenericNetworkTest):
    PROXY = False

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self, web_socket=True)

        # deploy the contract
        error = Error(self, web3)
        error.deploy(network, account)

        # force a require
        try:
            self.log.info('Forcing a require on contract function')
            error.contract.functions.force_require().call()
        except Exception as e:
            self.log.info('Exception type: %s', type(e).__name__)
            self.log.info('Exception args: %s', e.args)
            regex = re.compile('execution reverted:.*Forced require', re.M)
            self.assertTrue(regex.search(e.args[0]) is not None)

        # force a revert
        try:
            self.log.info('Forcing a revert on contract function')
            error.contract.functions.force_revert().call()
        except Exception as e:
            self.log.info('Exception type: %s', type(e).__name__)
            self.log.info('Exception args: %s', e.args)
            regex = re.compile('execution reverted:.*Forced revert', re.M)
            self.assertTrue(regex.search(e.args[0]) is not None)

        # force assert (note this fails on ganache)
        try:
            self.log.info('Forcing an assert on contract function')
            error.contract.functions.force_assert().call()
        except Exception as e:
            self.log.info('Exception type: %s', type(e).__name__)
            self.log.info('Exception args: %s', e.args)
            regex = re.compile('Assert evaluates to false', re.M)
            self.assertTrue(regex.search(e.args[0]) is not None)
