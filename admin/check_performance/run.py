import os
from datetime import datetime
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):

    def execute(self):
        tests = ['ten_per_001','ten_per_002','ten_per_003','ten_per_004','ten_per_005',
                 'ten_per_006','ten_per_007','ten_per_008','ten_per_009']

        for test in tests:
            with open(os.path.join(self.output, '%s.log' % test), 'w') as fp:
                for entry in reversed(self.results_db.get_results(test=test, environment=self.env)):
                    fp.write('%s %s\n' % (entry[0], entry[1]))
        self.graph()

    def graph(self):
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'), branch, date, str(self.mode))

