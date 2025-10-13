import os
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        self.stats_db.dump(file=os.path.join(self.output, 'stats.dmp'))
