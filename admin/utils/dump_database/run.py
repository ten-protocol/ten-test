import os
from ten.test.basetest import TenNetworkTest
from ten.test.persistence.results import OutcomeResultsPersistence


class PySysTest(TenNetworkTest):

    def execute(self):
        self.outcomes_db = OutcomeResultsPersistence.init(True, self.user_dir, self.machine_name)

        #self.rates_db.dump(file=os.path.join(self.output, 'stats.dmp'))
        #self.nonce_db.dump(file=os.path.join(self.output, 'stats.dmp'))
        #self.contract_db.dump(file=os.path.join(self.output, 'stats.dmp'))
        #self.funds_db.dump(file=os.path.join(self.output, 'stats.dmp'))
        #self.pandl_db.dump(file=os.path.join(self.output, 'stats.dmp'))
        #self.gas_db.dump(file=os.path.join(self.output, 'stats.dmp'))
        #self.counts_db.dump(file=os.path.join(self.output, 'stats.dmp'))

        self.stats_db.dump(file=os.path.join(self.output, 'stats.dmp'))
        self.results_db.dump(file=os.path.join(self.output, 'results_performance.dmp'))
        self.txcosts_db.dump(file=os.path.join(self.output, 'tx_costs.dmp'))
        self.runtype_db.dump(file=os.path.join(self.output, 'results_type.dmp'))
        self.outcomes_db.dump(file=os.path.join(self.output, 'results_outcome.dmp'))