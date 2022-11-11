from obscuro.test.basetest import ObscuroNetworkTest


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        num_transactions = self.get_num_transactions()
        self.log.info('Number of transactions is %d' % num_transactions)

        self.log.info('Last 5 transactions are;')
        for tx in self.get_latest_transactions(5):
            self.log.info('  %s' % tx)