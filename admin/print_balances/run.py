from pysys.constants import LOG_TRACEBACK
from pysys.utils.logutils import BaseLogFormatter
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)

        if not self.is_obscuro(): # on obscuro the funded account is used by the faucet so we don't want to connect
            self.log.info("")
            self.log.info("Checking funds for %s:", "funded_account_pk", extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
            network.connect(self, Properties().funded_account_pk(self.env), check_funds=False)

        for fn in Properties().accounts():
            self.log.info("")
            self.log.info("Checking funds for %s:", fn.__name__, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
            network.connect(self, fn(), check_funds=False)

