import os, time, re, math
from datetime import datetime
from collections import OrderedDict
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 1024         # number of iterations per client
    SENDING_ACCOUNTS = 20     # the number of sending accounts used by each client
    RECEIVING_ACCOUNTS = 20   # the number of recipient accounts receiving the funds

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.gas_price = 0
        self.gas_limit = 0
        self.chain_id = 0
        self.value = 100
        self.clients = ['one', 'two']
        self.expr1 = re.compile('Time to send all transactions was (?P<all>.*)$', re.M)
        self.expr2 = re.compile('Time to wait for last transaction was (?P<last>.*)$', re.M)
        self.expr3 = re.compile('Average time to wait for transaction receipt was (?P<avg>.*)$', re.M)

    def execute(self):
        all, last, avg = (None, None, None)

        # connect to the network on the primary gateway and calculate funds needs
        network = self.get_network_connection(name='local' if self.is_local_ten() else 'primary', verbose=False)
        web3, _ = network.connect_account1(self)
        account = web3.eth.account.from_key(self.get_ephemeral_pk())
        self.chain_id = network.chain_id()
        self.gas_price = web3.eth.gas_price
        self.gas_limit = web3.eth.estimate_gas({'to': account.address, 'value': self.value, 'gasPrice': self.gas_price})
        funds_needed = 1.1 * self.ITERATIONS * (self.gas_price*self.gas_limit + self.value)

        # run the clients
        pk_file1, conn1 = self.setup_client('client_one', funds_needed)
        pk_file2, conn2 = self.setup_client('client_two', funds_needed)
        self.run_client('client_one', pk_file1, conn1)
        self.run_client('client_two', pk_file2, conn2)
        txs_sent = 0
        for i in self.clients:
            self.log.info('Processing client %s' % i)
            stdout = os.path.join(self.output,'client_%s.out' % i)
            self.waitForGrep(file=stdout, expr='Client client_%s completed' % i, timeout=900)
            self.assertGrep(file=stdout, expr='Error sending raw transaction', contains=False, abortOnError=False)
            with open(stdout, 'r') as fp:
                for line in fp.readlines():
                    result1 = self.expr1.search(line)
                    result2 = self.expr2.search(line)
                    result3 = self.expr3.search(line)
                    if result1 is not None: all = result1.group('all')
                    if result2 is not None: last = result2.group('last')
                    if result3 is not None: avg = result3.group('avg')
            self.log.info('  Time to bulk send the raw transactions was %s' % all)
            self.log.info('  Time to wait for last tx receipt was %s' % last)
            self.log.info('  Average time to wait for a tx receipt was %s' % avg)
            txs_sent += self.txs_sent(file=stdout)

        # process and graph the output for the block timestamps
        data_timestamps = [self.load_timestamp_data('client_%s.log' % i) for i in self.clients]
        first = int(data_timestamps[0][0][1])
        last = int(data_timestamps[-1][-1][1])

        data_binned = [self.bin_timestamp_data(first, last, d, OrderedDict()) for d in data_timestamps]
        for i in self.clients:
            with open(os.path.join(self.output, 'client_%s.bin' % i), 'w') as fp:
                for key, value in data_binned[self.clients.index(i)].items(): fp.write('%d %d\n' % (key, value))

        with open(os.path.join(self.output, 'clients.bin'), 'w') as fp:
            for t in range(0, last + 1 - first):
                fp.write('%d %d\n' % (t, sum([d[t] for d in data_binned])))

        # process and graph the output for the tx receipt times
        l = []
        for i in self.clients: l.extend(self.load_duration_data('client_%s.log' % i))
        l.sort()
        bins = OrderedDict()
        bin_inc = 20  # 0.05 intervals
        bin = lambda x: int(math.floor(bin_inc*x))

        for i in range(bin(l[0]), bin(l[len(l)-1])+1): bins[i] = 0
        for v in l: bins[bin(v)] = bins[bin(v)] + 1
        with open(os.path.join(self.output, 'clients_receipt_times.bin'), 'w') as fp:
            for k in bins.keys(): fp.write('%.2f %d\n' % (k/float(bin_inc), bins[k]))
            fp.flush()

        branch = GnuplotHelper.buildInfo().branch
        duration = last - first
        average = float(txs_sent) / float(duration) if duration != 0 else 0
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(txs_sent), str(duration), '%.3f' % average)

        # persist the result
        if self.PERSIST_PERF:
            self.results_db.insert_result(self.descriptor.id, self.mode, int(time.time()), average)

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def setup_client(self, name, funds_needed):
        pk_file = '%s_pk.txt' % name
        network = self.get_network_connection(name='local' if self.is_local_ten() else 'primary', verbose=False)
        with open(os.path.join(self.output, pk_file), 'w') as fw:
            for i in range(0, self.SENDING_ACCOUNTS):
                pk = self.get_ephemeral_pk()
                web3, account = network.connect(self, private_key=pk, check_funds=False)
                self.distribute_native(account, web3.from_wei(funds_needed, 'ether'))
                fw.write('%s\n' % pk)
                fw.flush()
        return pk_file, network

    def run_client(self, name, pk_file, network):
        """Run a background load client. """
        stdout = os.path.join(self.output, '%s.out' % name)
        stderr = os.path.join(self.output, '%s.err' % name)
        script = os.path.join(self.input, 'client.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--chainId', '%s' % network.chain_id()])
        args.extend(['--pk_file', pk_file])
        args.extend(['--num_accounts', '%d' % self.RECEIVING_ACCOUNTS])
        args.extend(['--num_iterations', '%d' % self.ITERATIONS])
        args.extend(['--client_name', name])
        args.extend(['--amount', '%d' % self.value])
        args.extend(['--gas_limit', '%d' % self.gas_limit])
        self.run_python(script, stdout, stderr, args)
        self.waitForSignal(file=stdout, expr='Starting client %s' % name)

    def load_timestamp_data(self, file):
        """Load a client transaction log into memory for the timestamp data. """
        data = []
        with open(os.path.join(self.output, file), 'r') as fp:
            for line in fp.readlines():
                nonce, _, timestamp, duration = line.split()
                data.append((nonce, int(timestamp)))
        return data

    def bin_timestamp_data(self, first, last, data, binned_data):
        """Bin a client transaction data and offset the time. """
        b = OrderedDict()
        for _, t in data: b[t] = 1 if t not in b else b[t] + 1
        for t in range(first, last + 1): binned_data[t - first] = 0 if t not in b else b[t]
        return binned_data

    def load_duration_data(self, file):
        """Load a client transaction log into memory for the tx receipt times. """
        data = []
        with open(os.path.join(self.output, file), 'r') as fp:
            for line in fp.readlines():
                _, _, _, duration = line.split()
                data.append(float(duration))
        return data
