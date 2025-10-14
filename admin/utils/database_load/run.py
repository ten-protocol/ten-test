import os
from ten.test.basetest import TenNetworkTest
from ten.test.persistence.results import OutcomeResultsPersistence
from ten.test.persistence.rates import RatesPersistence
from ten.test.persistence.counts import CountsPersistence
from ten.test.persistence.stats import StatsPersistence
from ten.test.persistence.funds import FundsPersistence, PandLPersistence, GasPricePersistence
from ten.test.persistence.results import PerformanceResultsPersistence, TxCostResultsPersistence, RunTypePersistence


class PySysTest(TenNetworkTest):
    REMOTE = False

    def execute(self):

        rates_db = RatesPersistence.init(self.REMOTE, self.user_dir, self.machine_name)
        funds_db = FundsPersistence.init(self.REMOTE, self.user_dir, self.machine_name)
        pandl_db = PandLPersistence.init(self.REMOTE, self.user_dir, self.machine_name)
        gas_db = GasPricePersistence.init(self.REMOTE, self.user_dir, self.machine_name)
        counts_db = CountsPersistence.init(self.REMOTE, self.user_dir, self.machine_name)
        stats_db = StatsPersistence.init(self.REMOTE, self.user_dir, self.machine_name)
        txcosts_db = TxCostResultsPersistence.init(self.REMOTE, self.user_dir, self.machine_name)
        results_db = PerformanceResultsPersistence.init(self.REMOTE, self.user_dir, self.machine_name)
        runtype_db = RunTypePersistence.init(self.REMOTE, self.user_dir, self.machine_name)
        outcomes_db = OutcomeResultsPersistence.init(self.REMOTE, self.user_dir, self.machine_name)

        self.load(rates_db, 'rates.sql')
        self.load(funds_db, 'funds.sql')
        self.load(pandl_db, 'pandl.sql')
        self.load(gas_db, 'gas_prices.sql')
        self.load(counts_db, 'counts.sql')
        self.load(stats_db, 'stats.sql')
        self.load(txcosts_db, 'tx_costs.sql')
        self.load(results_db, 'results_performance.sql')
        self.load(runtype_db, 'results_type.sql')
        self.load(outcomes_db, 'results_outcome.sql')

    def load(self, db, filename):
        with open(os.path.join(self.input, filename), 'w') as fp:
            for e in fp.readlines(): db.cursor.execute(e)
        db.dbconnection.connection.commit()