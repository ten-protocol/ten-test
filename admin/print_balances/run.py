from pysys.constants import LOG_TRACEBACK
from pysys.utils.logutils import BaseLogFormatter
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        network = NetworkFactory.get_network(self)
        for fn in Properties().accounts():
            self.log.info("")
            self.log.info("Checking funds for %s:", fn.__name__, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
            network.connect(self, fn(), check_funds=False)

