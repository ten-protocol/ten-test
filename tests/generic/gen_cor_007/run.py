import re
from ethsys.basetest import EthereumTest
from ethsys.contracts.error.error import Error
from ethsys.networks.factory import NetworkFactory


class PySysTest(EthereumTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1()

        error = Error(self, web3, 'foo')
        error.deploy(network, account)

        # force a require
        try:
            error.contract.functions.force_require().call()
        except Exception as e:
            self.log.info('Exception type: %s' % type(e).__name__)
            self.log.info('Exception args: %s' % e.args[0])
            regex = re.compile('execution reverted:.*Forced require', re.M)
            self.assertTrue(regex.search(e.args[0]) is not None)

        # force a revert
        try:
            error.contract.functions.force_revert().call()
        except Exception as e:
            self.log.info('Exception type: %s' % type(e).__name__)
            self.log.info('Exception args: %s' % e.args[0])
            regex = re.compile('execution reverted:.*Forced revert', re.M)
            self.assertTrue(regex.search(e.args[0]) is not None)

        # force assert
        try:
            error.contract.functions.force_assert().call()
        except Exception as e:
            self.log.info('Exception type: %s' % type(e).__name__)
            self.log.info('Exception args: %s' % e.args[0])
            regex = re.compile('execution reverted', re.M)
            self.assertTrue(regex.search(e.args[0]) is not None)