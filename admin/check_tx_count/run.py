import time
from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        current_time = int(time.time())
        network = self.get_l1_network_connection(self.env)
        url = network.connection_url()
        web3 = Web3(Web3.HTTPProvider(url))

        # recorded last then get last two hours of recorded tx counts - note that we expect a regular interval of
        # recordings which might not be the case if the job is queued or stopped at any point
        sequencer_address = Properties().sequencer_address(key=self.env)
        sequencer_count = web3.eth.get_transaction_count(sequencer_address)
        self.log.info('Sequencer tx count %d', sequencer_count)
        self.counts_db.insert_count('Sequencer', sequencer_address, self.env, current_time, sequencer_count)
        entries = self.counts_db.get_last_hour('Sequencer', sequencer_address, self.env, current_time - 7200)

        # make sure we have at least 2 entries recorded within the last two hours
        if len(entries) >= 2:

            # make sure of those recorded there is at least a one hour difference between the first and last
            if (entries[0][0] - entries[-1][0]) >= 3600:
                self.log.info('Retrieved counts;')
                for entry in entries: self.log.info('  %s %s', entry[0], entry[1])

                # assert on there being a difference in the tx count for this period
                self.assertTrue(int(entries[0][1]) > int(entries[-1][1]), assertMessage='Check increase in the tx count seen')

            else:
                self.log.warn('Less than 1 hour recorded between retrieved entries ... skipping')

        else:
            self.log.warn('Less than 2 entries recorded over the last 2 hour period ... skipping')

