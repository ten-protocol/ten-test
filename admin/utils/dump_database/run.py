import os
from ten.test.basetest import TenNetworkTest
from ten.test.persistence.results import OutcomeResultsPersistence


class PySysTest(TenNetworkTest):

    def execute(self):
        self.outcomes_db = OutcomeResultsPersistence.init(True, self.user_dir, self.machine_name)

        self.rates_db.dump(file=os.path.join(self.output, 'rates.dmp'))
        self.funds_db.dump(file=os.path.join(self.output, 'funds.dmp'))
        self.pandl_db.dump(file=os.path.join(self.output, 'pandl.dmp'))
        self.gas_db.dump(file=os.path.join(self.output, 'gas_prices.dmp'))
        self.counts_db.dump(file=os.path.join(self.output, 'counts.dmp'))
        self.stats_db.dump(file=os.path.join(self.output, 'stats.dmp'))
        self.txcosts_db.dump(file=os.path.join(self.output, 'tx_costs.dmp'))
        self.results_db.dump(file=os.path.join(self.output, 'results_performance.dmp'))
        self.runtype_db.dump(file=os.path.join(self.output, 'results_type.dmp'))
        self.outcomes_db.dump(file=os.path.join(self.output, 'results_outcome.dmp'))
