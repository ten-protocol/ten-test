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

        rates_db.serialise(file=os.path.join(self.output, 'rates.csv'))
        funds_db.serialise(file=os.path.join(self.output, 'funds.csv'))
        pandl_db.serialise(file=os.path.join(self.output, 'pandl.csv'))
        gas_db.serialise(file=os.path.join(self.output, 'gas_prices.csv'))
        counts_db.serialise(file=os.path.join(self.output, 'counts.csv'))
        stats_db.serialise(file=os.path.join(self.output, 'stats.csv'))
        txcosts_db.serialise(file=os.path.join(self.output, 'tx_costs.csv'))
        results_db.serialise(file=os.path.join(self.output, 'results_performance.csv'))
        runtype_db.serialise(file=os.path.join(self.output, 'results_type.csv'))
        outcomes_db.serialise(file=os.path.join(self.output, 'results_outcome.csv'))
