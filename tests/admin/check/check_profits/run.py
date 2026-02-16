import time, os
from datetime import datetime
from collections import OrderedDict
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper
from ten.test.persistence.funds import FundsPersistence, PandLPersistence

class PySysTest(TenNetworkTest):

    def execute(self):
        # databases to use
        self.funds_db = FundsPersistence(self.use_remote(), self.user_dir, self.machine_name)
        self.pandl_db = PandLPersistence(self.use_remote(), self.user_dir, self.machine_name)
        self.addCleanupFunction(self.close_db_connections)

        with open(os.path.join(self.output, 'sequencer_funds.log'), 'w') as fp:
            for entry in reversed(self.funds_db.get_funds(name='Sequencer', environment=self.env)):
                fp.write('%s %s\n' % (entry[0], entry[1]))

        with open(os.path.join(self.output, 'gas_payment.log'), 'w') as fp:
            for entry in reversed(self.funds_db.get_funds(name='GasPayment', environment=self.env)):
                fp.write('%s %s\n' % (entry[0],  entry[1]))

        last_time = self.pandl_db.get_latest_timestamp(environment=self.env)
        self.graph(last_time)

        # pass if no errors
        self.addOutcome(PASSED)

    def graph(self, last_time):
        dict = OrderedDict()

        last_value = 0
        running_total = 0
        with open(os.path.join(self.output, 'sequencer_funds.log'), 'r') as fp:
            for line in fp.readlines():
                time = int(line.split()[0])
                value = int(line.split()[1])
                if value > last_value: last_value = value
                running_total = running_total + (value - last_value)
                if not time in dict: dict[time] = (running_total, None)
                last_value = value

        last_value = 0
        running_total = 0
        with open(os.path.join(self.output, 'gas_payment.log'), 'r') as fp:
            for line in fp.readlines():
                time = int(line.split()[0])
                value = int(line.split()[1])
                if value < last_value: last_value = value
                running_total = running_total + (value - last_value)
                if not time in dict: dict[time] = (None, running_total)
                else: dict[time] = (dict[time][0], running_total)
                last_value = value

        times = [t for t in dict.keys() if (dict[time][0] is not None) and (dict[time][1] is not None)]
        sequencer_start = dict[times[0]][0]
        gas_payment_start = dict[times[0]][1]
        with open(os.path.join(self.output, 'profits.log'), 'w') as fp:
            fp.write('%d %d %d %d\n' % (times[0], 0, 0, 0))
            for t in times[1:]:
                sequencer_diff = dict[t][0] - sequencer_start
                gas_payment_diff = dict[t][1] - gas_payment_start
                pandl = gas_payment_diff + sequencer_diff
                fp.write('%d %d %d %d\n' % (t, sequencer_diff, gas_payment_diff, pandl))
                if t > last_time:
                    self.log.info('Last time = %d, entry time = %d, saving to the pandl db' % (last_time, t))
                    self.pandl_db.insert_pandl(self.env, t, sequencer_diff/1e18, gas_payment_diff/1e18, pandl/1e18)

        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'), branch, date, str(self.mode))

    def close_db_connections(self):
        self.funds_db.close()
        self.pandl_db.close()