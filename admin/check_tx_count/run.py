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

        sequencer_address = Properties().sequencer_address(key='ten.sepolia')
        sequencer_count = web3.eth.get_transaction_count(sequencer_address)

        self.log.info('Sequencer tx count %d', sequencer_count)
        self.counts_db.insert_count('Sequencer', sequencer_address, self.env, current_time, sequencer_count)

        entries = self.counts_db.get_last_three_counts('Sequencer', self.env)
        self.log.info('Last three counts;')
        for entry in entries: self.log.info('%s %s', (entry[0], entry[1]))
