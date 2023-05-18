from pysys.constants import LOG_TRACEBACK
from pysys.utils.logutils import BaseLogFormatter
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        self.log.info('Removing entries for environment %s' % self.env)
        self.nonce_db.delete_environment(self.env)

        network = NetworkFactory.get_network(self)
        for fn in Properties().accounts(): self.reset(fn.__name__, *network.connect(self, fn(), check_funds=False))

    def reset(self, name, web3, account):
        self.log.info("")
        self.log.info("Resetting persistence for  %s:", name, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
        count = web3.eth.get_transaction_count(account.address)  # count is what the next would be
        self.log.info('Account %s transaction count is %d' % (account.address, count))
        if count > 0:
            self.log.info('Account %s updating last persisted nonce to %d' % (account.address, count-1))
            self.nonce_db.insert(account.address, self.env, count-1, 'RESET')