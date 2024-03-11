import os, time, secrets, sys
import numpy as np
from datetime import datetime
from collections import OrderedDict
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 1024      # iterations per client
    ACCOUNTS = 8           # number of different accounts that receive the funds per client

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.gas_price = 0
        self.gas_limit = 0
        self.chain_id = 0
        self.value = 100

    def execute(self):
        # connect to the network on the primary gateway and calculate funds needs
        network = self.get_network_connection()
        web3, _ = network.connect_account1(self)
        account = web3.eth.account.from_key(secrets.token_hex(32))
        self.chain_id = network.chain_id()
        self.gas_price = web3.eth.gas_price
        self.gas_limit = web3.eth.estimate_gas({'to': account.address, 'value': self.value, 'gasPrice': self.gas_price})
        funds_needed = 1.1 * self.ITERATIONS * (self.gas_price*self.gas_limit + self.value)

        # run the clients and wait for their completion
        results_file = os.path.join(self.output, 'results.log')
        with open(results_file, 'w') as fp:
            for clients in [2,3,4,5]:
                self.log.info(' ')
                self.log.info('Running for %d clients' % clients)

                out_dir = os.path.join(self.output, 'clients_%d' % clients)
                signal = os.path.join(out_dir, '.signal')
                for i in range(0, clients):
                    self.run_client('client_%s' % i, funds_needed, out_dir, signal)

                start_ns = time.perf_counter_ns()
                with open(signal, 'w') as sig: sig.write('go')
                for i in range(0, clients):
                    self.waitForGrep(file=os.path.join(out_dir, 'client_%s.out' % i),
                                     expr='Client client_%s completed' % i, timeout=300)
                end_ns = time.perf_counter_ns()

                bulk_throughput = float(clients * self.ITERATIONS) / float((end_ns - start_ns) / 1e9)
                throughput = self.process_throughput(clients, out_dir)
                self.log.info('Bulk rate throughput %.2f (requests/sec)' % bulk_throughput)
                self.log.info('Approx. throughput %.2f (requests/sec)' % throughput)
                fp.write('%d %.2f\n' % (clients, throughput))

        # plot the summary graph
        self.graph_all_clients()

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def run_client(self, name, funds_needed, out_dir, signal_file):
        """Run a background load client. """
        pk = secrets.token_hex(32)
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, web3.from_wei(funds_needed, 'ether'))

        if not os.path.exists(out_dir): os.mkdir(out_dir)
        stdout = os.path.join(out_dir, '%s.out' % name)
        stderr = os.path.join(out_dir, '%s.err' % name)
        script = os.path.join(self.input, 'client.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--chainId', '%s' % network.chain_id()])
        args.extend(['--pk', pk])
        args.extend(['--num_accounts', '%d' % self.ACCOUNTS])
        args.extend(['--num_iterations', '%d' % self.ITERATIONS])
        args.extend(['--client_name', name])
        args.extend(['--amount', '%d' % self.value])
        args.extend(['--gas_limit', '%d' % self.gas_limit])
        args.extend(['--signal_file', signal_file])
        self.run_python(script, stdout, stderr, args, workingDir=out_dir)
        self.waitForSignal(file=stdout, expr='Starting client %s' % name)

    def process_throughput(self, num_clients, out_dir):
        # store the binned data for each client and the timestamps
        start_time = sys.maxsize
        end_time = 0
        throughput = 0
        list_client_bins = []
        list_client_times = []
        for i in range(0, num_clients):
            client_bins = OrderedDict()
            with open(os.path.join(out_dir, 'client_%s_throughput.log' % i), 'r') as fp:
                for line in fp.readlines():
                    timestamp = int(line.strip())
                    if timestamp < start_time: start_time = timestamp
                    if timestamp > end_time: end_time = timestamp
                    if timestamp not in client_bins: client_bins[timestamp] = 0
                    else: client_bins[timestamp] = client_bins[timestamp] + 1
                list_client_bins.append(client_bins)
                list_client_times.append(list(client_bins.keys()))

        # bin the data
        bins = OrderedDict()
        for x in range(start_time, end_time + 1): bins[x] = 0
        for client_bins in list_client_bins:
            for timestamp in client_bins.keys():
                bins[timestamp] = bins[timestamp] + client_bins[timestamp]

        # reduce to the overlap and find best zero gradient fit
        min, max = self.find_overlap(list_client_times)
        included = [i for i in range(min, max+1, 1)]
        if len(included) > 0:
            bins_steady = {key: value for key, value in bins.items() if key in included}
            bins_ramp = {key: value for key, value in bins.items() if key not in included}
            throughput = float(sum(bins_steady.values())) / float((included[-1] - included[0]))

            with open(os.path.join(out_dir, 'binned_throughput_all.log'), 'w') as fp:
                for t in bins.keys(): fp.write('%d %d\n' % (t-start_time, bins[t]))

            with open(os.path.join(out_dir, 'binned_throughput_steady.log'), 'w') as fp:
                for t in bins_steady.keys(): fp.write('%d %d %.2f\n' % (t-start_time, bins_steady[t], throughput))

            with open(os.path.join(out_dir, 'binned_throughput_ramp.log'), 'w') as fp:
                for t in bins_ramp.keys(): fp.write('%d %d\n' % (t-start_time, bins_ramp[t]))
        else:
            self.log.warn('No overlap of all clients detected')

        return throughput

    def graph_all_clients(self):
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'), branch, date, str(self.mode))

    def find_overlap(self, lists):
        if len(lists) == 0: return []
        overlap = np.array(lists[0])
        for l in lists[1:]: overlap = np.intersect1d(overlap, np.array(l))
        return overlap.tolist()[0], overlap.tolist()[-1]

