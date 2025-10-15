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
        if self.REMOTE: self.log.warn('Running dump against the remote database')

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

        self.load(rates_db, 'rates.csv')
        self.load(funds_db, 'funds.csv')
        self.load(pandl_db, 'pandl.csv')
        self.load(gas_db, 'gas_prices.csv')
        self.load(counts_db, 'counts.csv')
        self.load(stats_db, 'stats.csv')
        self.load(txcosts_db, 'tx_costs.csv')
        self.load(results_db, 'results_performance.csv')
        self.load(runtype_db, 'results_type.csv')
        self.load(outcomes_db, 'results_outcome.csv')

    def load(self, db, filename):
        path = os.path.join(self.input, filename)
        if os.path.exists(path):
            self.log.info('Loading data from input file %s' % filename)
            db.load(path)
        else:
            self.log.warn('Input file %s does not exist' % filename)

