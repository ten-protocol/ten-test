import os
from ten.test.basetest import TenNetworkTest
from ten.test.persistence.results import OutcomeResultsPersistence


class PySysTest(TenNetworkTest):

    def execute(self):
        self.outcomes_db = OutcomeResultsPersistence.init(True, self.user_dir, self.machine_name)

        self.rates_db.dump(file=os.path.join(self.output, 'rates.sql'))
        self.funds_db.dump(file=os.path.join(self.output, 'funds.sql'))
        self.pandl_db.dump(file=os.path.join(self.output, 'pandl.sql'))
        self.gas_db.dump(file=os.path.join(self.output, 'gas_prices.sql'))
        self.counts_db.dump(file=os.path.join(self.output, 'counts.sql'))
        self.stats_db.dump(file=os.path.join(self.output, 'stats.sql'))
        self.txcosts_db.dump(file=os.path.join(self.output, 'tx_costs.sql'))
        self.results_db.dump(file=os.path.join(self.output, 'results_performance.sql'))
        self.runtype_db.dump(file=os.path.join(self.output, 'results_type.sql'))
        self.outcomes_db.dump(file=os.path.join(self.output, 'results_outcome.sql'))
