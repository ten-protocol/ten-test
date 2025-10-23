import requests, json, time
from web3 import Web3
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties


class PySysTest(TenNetworkTest):

    def execute(self):
        current_time = int(time.time())
        l1_network = self.get_l1_network_connection(self.env)
        web3_l1, account_l1 = l1_network.connect_account1(self)
        l2_network = self.get_network_connection()
        web3_l2, account_l2 = l2_network.connect_account1(self)

        # store the sequencer balance and tx count (on the L1)
        sequencer_address = Properties().sequencer_address(key=self.env)
        sequencer_balance = web3_l1.eth.get_balance(sequencer_address)
        sequencer_count = web3_l1.eth.get_transaction_count(sequencer_address)
        self.log.info('Using sequencer address %s' % sequencer_address)
        self.log.info('Sequencer balance %.9f ETH', web3_l1.from_wei(sequencer_balance, 'ether'))
        self.funds_db.insert_funds('Sequencer', sequencer_address, self.env, current_time, sequencer_balance)
        self.log.info('Sequencer tx count %d', sequencer_count)
        self.counts_db.insert_count('Sequencer', sequencer_address, self.env, current_time, sequencer_count)

        # store the bridge balance (on the l1)
        bridge_address = Properties().l1_bridge_address()
        bridge_balance_wei = web3_l1.eth.get_balance(bridge_address)
        faucet_balance_eth = web3_l1.from_wei(bridge_balance_wei, 'ether')
        self.log.info('Using bridge address %s' % bridge_address)
        self.log.info('Bridge balance %.9f ETH', faucet_balance_eth)
        self.funds_db.insert_funds('L1Bridge', bridge_address, self.env, current_time, bridge_balance_wei)

        # store the gas holding account balance (on the L2)
        gas_payment_address = Properties().l2_gas_payment_address(self.env)
        gas_payment_balance = web3_l2.eth.get_balance(gas_payment_address)
        self.log.info('Gas holding balance %.9f ETH', web3_l2.from_wei(gas_payment_balance, 'ether'))
        self.funds_db.insert_funds('GasPayment', gas_payment_address, self.env, current_time, gas_payment_balance)

        # store the faucet balance (on the L2 via the faucet end point)
        faucet_address = Properties().faucet_address(key=self.env)
        faucet_balance_wei = self.get_faucet_balance()
        faucet_balance_eth = Web3().from_wei(faucet_balance_wei, 'ether')
        self.log.info('Faucet balance %.9f ETH', faucet_balance_eth)
        self.funds_db.insert_funds('Faucet', faucet_address, self.env, current_time, faucet_balance_wei)

        # store the total transaction count (on the L2 via the tenscan API)
        last_result = self.stats_db.get_last_entry(self.env, 'transactions')
        current_value = self.scan_get_total_transaction_count()
        last_value = 0 if last_result is None else int(last_result[0])
        last_running = 0 if last_result is None else int(last_result[1])
        delta = 0 if (current_value-last_value) < 0 else (current_value-last_value)
        self.log.info('Transaction count, value=%d, delta=%d, running total=%d' % (current_value, delta, (last_running+delta)))
        self.stats_db.insert(self.env, current_time, 'transactions', current_value, delta, last_running+delta)

        # store the total contract count (on the L2 via the tenscan API)
        last_result = self.stats_db.get_last_entry(self.env, 'contracts')
        current_value = self.scan_get_total_contract_count()
        last_value = 0 if last_result is None else int(last_result[0])
        last_running = 0 if last_result is None else int(last_result[1])
        delta = 0 if (current_value-last_value) < 0 else (current_value-last_value)
        self.log.info('Contract count, value=%d, delta=%d, running total=%d' % (current_value, delta, (last_running+delta)))
        self.stats_db.insert(self.env, current_time, 'contracts', current_value, delta, last_running+delta)

        # pass if no errors
        self.addOutcome(PASSED)

    def get_faucet_balance(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '%s/balance' % Properties().faucet_host(self.env)
        response = requests.get(url, headers=headers)
        response_data = json.loads(response.text)
        return int(response_data.get('balance'))

