import requests, json, time
from web3 import Web3
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        current_time = int(time.time())
        l1_network = self.get_l1_network_connection(self.env)
        web3, account = l1_network.connect_account1(self)

        # store the bridge balance
        bridge_address = Properties().l1_bridge_address()
        bridge_balance_wei = web3.eth.get_balance(bridge_address)
        faucet_balance_eth = web3.from_wei(bridge_balance_wei, 'ether')
        self.log.info('Bridge balance %.9f ETH', faucet_balance_eth)
        self.funds_db.insert_funds('L1Bridge', bridge_address, self.env, current_time, bridge_balance_wei)

        # store the faucet balance
        faucet_address = Properties().faucet_address(key=self.env)
        faucet_balance_wei = self.get_faucet_balance()
        faucet_balance_eth = Web3().from_wei(faucet_balance_wei, 'ether')
        self.log.info('Faucet balance %.9f ETH', faucet_balance_eth)
        self.funds_db.insert_funds('Faucet', faucet_address, self.env, current_time, faucet_balance_wei)

        # store the total transaction count
        last_result = self.stats_db.get_last_entry(self.env, 'transactions')
        current_value = self.scan_get_total_transaction_count()
        last_value = 0 if last_result is None else int(last_result[0])
        last_running = 0 if last_result is None else int(last_result[1])
        delta = 0 if (current_value-last_value) < 0 else (current_value-last_value)
        self.log.info('Transaction count, value=%d, delta=%d, running total=%d' % (current_value, delta, (last_running+delta)))
        self.stats_db.insert(self.env, current_time, 'transactions', current_value, delta, last_running+delta)

        # store the total contract count
        last_result = self.stats_db.get_last_entry(self.env, 'contracts')
        current_value = self.scan_get_total_contract_count()
        last_value = 0 if last_result is None else int(last_result[0])
        last_running = 0 if last_result is None else int(last_result[1])
        delta = 0 if (current_value-last_value) < 0 else (current_value-last_value)
        self.log.info('Contract count, value=%d, delta=%d, running total=%d' % (current_value, delta, (last_running+delta)))
        self.stats_db.insert(self.env, current_time, 'contracts', current_value, delta, last_running+delta)

    def get_faucet_balance(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '%s/balance' % Properties().faucet_host(self.env)
        response = requests.get(url, headers=headers)
        response_data = json.loads(response.text)
        return int(response_data.get('balance'))

