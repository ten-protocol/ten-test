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

        # store the bridge balance
        bridge_address = Properties().l1_bridge_address()
        bridge_balance_wei = web3.eth.get_balance(bridge_address)
        faucet_balance_eth = web3.from_wei(bridge_balance_wei, 'ether')
        self.log.info('Bridge balance %.9f ETH', faucet_balance_eth)
        self.funds_db.insert_funds('L1Bridge', bridge_address, self.env, current_time, bridge_balance_wei)
