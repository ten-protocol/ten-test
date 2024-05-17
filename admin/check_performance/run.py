import time, os
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        tests = ['ten_per_001','ten_per_002','ten_per_003','ten_per_04','ten_per_005',
                 'ten_per_006','ten_per_007','ten_per_008','ten_per_009']

        for test in tests:
            with open(os.path.join(self.output, '%s.log' % test), 'w') as fp:
                for entry in reversed(self.results_db.get_results(test=test, environment='ten.uat')):
                    fp.write('%s %s\n' % (entry[0], entry[1]))
