from pysys.constants import LOG_TRACEBACK
from pysys.utils.logutils import BaseLogFormatter
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):

    def execute(self):

        if self.is_obscuro():
            self.log.info("")
            network = self.get_l1_network_connection()
            self.log.info("Checking funds for %s:", "l1_funded_account_pk", extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
            web3, account = network.connect(self, Properties().l1_funded_account_pk(self.env), check_funds=False, verbose=False)
            balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
            self.log.info('Account %s balance %.6f ETH', account.address, balance)
            self.log.info("")

        network = self.get_network_connection()
        for fn in Properties().accounts():
            self.log.info("")
            self.log.info("Checking funds for %s:", fn.__name__, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
            web3, account = network.connect(self, fn(), check_funds=False, verbose=False)
            balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
            self.log.info('Account %s balance %.6f ETH', account.address, balance)

