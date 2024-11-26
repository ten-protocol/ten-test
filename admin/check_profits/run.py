import time, os, shutil
from web3 import Web3
from datetime import datetime
from collections import OrderedDict
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):

    def execute(self):
        self.execute_run()

    def execute_run(self):
        current_time = int(time.time())

        l1_network = self.get_l1_network_connection(self.env)
        web3_sequencer = Web3(Web3.HTTPProvider(l1_network.connection_url()))
        sequencer_address = Properties().sequencer_address(key='ten.sepolia')
        sequencer_balance = web3_sequencer.eth.get_balance(sequencer_address)
        self.log.info('Sequencer balance %.9f ETH', web3_sequencer.from_wei(sequencer_balance, 'ether'))
        self.funds_db.insert_funds('Sequencer', sequencer_address, self.env, current_time, sequencer_balance)

        l2_network = self.get_network_connection()
        web3_payment, account_payment = l2_network.connect(self, Properties().l2_gas_payment_account_pk(self.env), check_funds=False)
        gas_payment_address = account_payment.address
        gas_payment_balance = web3_payment.eth.get_balance(gas_payment_address)
        self.log.info('Gas holding balance %.9f ETH', web3_sequencer.from_wei(gas_payment_balance, 'ether'))
        self.funds_db.insert_funds('GasPayment', gas_payment_address, self.env, current_time, gas_payment_balance)

        with open(os.path.join(self.output, 'sequencer_funds.log'), 'w') as fp:
            for entry in reversed(self.funds_db.get_funds(name='Sequencer', environment=self.env)):
                fp.write('%s %s\n' % (entry[0], entry[1]))

        with open(os.path.join(self.output, 'gas_payment.log'), 'w') as fp:
            for entry in reversed(self.funds_db.get_funds(name='GasPayment', environment=self.env)):
                fp.write('%s %s\n' % (entry[0],  entry[1]))

        self.graph()

    def execute_graph(self):
        shutil.copy(os.path.join(self.input, 'gas_payment.log'), os.path.join(self.output, 'gas_payment.log'))
        shutil.copy(os.path.join(self.input, 'sequencer_funds.log'), os.path.join(self.output, 'sequencer_funds.log'))
        self.graph()

    def graph(self):
        dict = OrderedDict()

        last_value = 0
        running_total = 0
        with open(os.path.join(self.output, 'sequencer_funds.log'), 'r') as fp:
            for line in fp.readlines():
                time = int(line.split()[0])
                value = int(line.split()[1])
                if value > last_value: last_value = value
                running_total = running_total + (value - last_value)
                if not time in dict: dict[time] = (running_total, None)
                last_value = value

        last_value = 0
        running_total = 0
        with open(os.path.join(self.output, 'gas_payment.log'), 'r') as fp:
            for line in fp.readlines():
                time = int(line.split()[0])
                value = int(line.split()[1])
                if value < last_value: last_value = value
                running_total = running_total + (value - last_value)
                if not time in dict: dict[time] = (None, running_total)
                else: dict[time] = (dict[time][0], running_total)
                last_value = value

        times = [t for t in dict.keys() if (dict[time][0] is not None) and (dict[time][1] is not None)]
        sequencer_start = dict[times[0]][0]
        gas_payment_start = dict[times[0]][1]
        with open(os.path.join(self.output, 'profits.log'), 'w') as fp:
            fp.write('%d %d %d %d\n' % (times[0], 0, 0, 0))
            for t in times[1:]:
                sequencer_diff = dict[t][0] - sequencer_start
                gas_payment_diff = dict[t][1] - gas_payment_start
                pandl = gas_payment_diff + sequencer_diff
                fp.write('%d %d %d %d\n' % (t, sequencer_diff, gas_payment_diff, pandl))

        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'), branch, date, str(self.mode))
