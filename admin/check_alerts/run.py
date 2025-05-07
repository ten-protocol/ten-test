import time
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        current_time = int(time.time())
        entries = self.runtype_db.get_last_two_results(self.env, 'health')

        ultimate = True if entries[0][1] == 1 else False
        penultimate = True if entries[1][1] == 1 else False
        if not ultimate and penultimate:
            # moved from passing (penultimate true) to failing (ultimate false)
            self.log.info('Health status has changed to failing')
        elif not penultimate and not ultimate:
            # moved from failing (penultimate false) to passing (ultimate true)
            self.log.info('Health status has changed to passing')
        elif penultimate and ultimate:
            # still passing
            self.log.info('In a run of passing checks ... no health change')
        elif not penultimate and not ultimate:
            # still failing
            self.log.info('In a run of failing checks ... no health change')
