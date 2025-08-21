import os
from datetime import datetime
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):

    def execute(self):
        tests = ['ten_per_001','ten_per_002','ten_per_003',
                 'ten_per_004','ten_per_005','ten_per_006',
                 'ten_per_007','ten_per_008',
                 'ten_per_010','ten_per_011','ten_per_012',
                 'ten_per_020','ten_per_021']

        for test in tests:
            with open(os.path.join(self.output, '%s.log' % test), 'w') as fp:
                entries = self.results_db.get_results(test=test, environment=self.env)
                if len(entries) > 1:
                    weights = [1 - (i / (len(entries) - 1)) * (1 - 0.1) for i in range(len(entries))]
                else: weights = [1]*len(entries)
                count = 0
                for entry in reversed(entries):
                    weight = weights[count]
                    fp.write('%s %s %s\n' % (self.epoch_to_fractional_doy(entry[0]), entry[1], weight))
                    count = count + 1
        try:
            self.graph()
        except Exception as e:
            self.log.warn('Exception raised when trying to graph results')
            self.log.warn(e)

    def graph(self):
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot_pg1.in'), branch, date, str(self.mode))
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot_pg2.in'), branch, date, str(self.mode))

    def epoch_to_fractional_doy(self, epoch_time):
        date = datetime.utcfromtimestamp(epoch_time)
        start_of_records = datetime(2024, 1, 1)
        delta = date - start_of_records
        fractional_doy = delta.days + (delta.seconds + delta.microseconds / 1e6) / 86400
        return fractional_doy
