import time
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.persistence.counts import CountsPersistence


class PySysTest(TenNetworkTest):

    def execute(self):
        current_time = int(time.time())

        # databases to use
        self.counts_db = CountsPersistence(self.use_remote(), self.user_dir, self.machine_name)
        self.addCleanupFunction(self.close_db_connections)

        # get last eight hours of recorded tx counts - note that we expect a regular interval of
        # recordings which might not be the case if the job is queued or stopped at any point
        sequencer_address = Properties().sequencer_address(key=self.env)
        entries = self.counts_db.get_since_time('Sequencer', sequencer_address, self.env, current_time - 28800)

        # make sure we have at least 4 entries recorded within the last six hours
        if len(entries) >= 4:

            # make sure of those recorded there is at least a six hour difference between the first and last
            if (entries[0][0] - entries[-1][0]) >= 21600:
                self.log.info('Retrieved counts;')
                for entry in entries: self.log.info('  %s %s', entry[0], entry[1])

                # assert on there being a difference in the tx count for this period
                self.assertTrue(int(entries[0][1]) > int(entries[-1][1]), assertMessage='Check increase in the tx count seen')

            else:
                self.log.warn('Less than 2 hours recorded between retrieved entries ... skipping')

        else:
            self.log.warn('Less than 2 entries recorded over the last 4 hour period ... skipping')

    def close_db_connections(self):
        self.counts_db.close()