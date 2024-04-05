import os, time, secrets, math
import numpy as np
from web3 import Web3
from datetime import datetime
from collections import OrderedDict
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 2*1024  # iterations per client

    def execute(self):
        # connect to the network and determine constants and funds required to run the test
        network = self.get_network_connection()

        # run the clients and wait for their completion
        results_file = os.path.join(self.output, 'results.log')
        with open(results_file, 'w') as fp:
            for clients in [1,2,3,4,6,8,10,12,16,20]:
                self.log.info(' ')
                self.log.info('Running for %d clients' % clients)
                out_dir = os.path.join(self.output, 'clients_%d' % clients)
                start_ns = time.perf_counter_ns()
                signal = os.path.join(out_dir, '.signal')
                for i in range(0, clients):
                    self.run_client('client_%s' % i, network, self.ITERATIONS, start_ns, out_dir, signal)

                with open(signal, 'w') as sig: sig.write('go')
                for i in range(0, clients):
                    self.waitForGrep(file=os.path.join(out_dir, 'client_%s.out' % i),
                                     expr='Client client_%s completed' % i, timeout=300)

                end_ns = time.perf_counter_ns()
                bulk_throughput = float(clients * self.ITERATIONS) / float((end_ns-start_ns)/1e9)
                avg_latency, mode_latency = self.process_latency(clients, out_dir)
                throughput = self.process_throughput(clients, out_dir, start_ns, end_ns)
                self.log.info('Bulk rate throughput %.2f (requests/sec)' % bulk_throughput)
                self.log.info('Approx. throughput %.2f (requests/sec)' % throughput)
                self.log.info('Average latency %.2f (ms)' % avg_latency)
                self.log.info('Modal latency %.2f (ms)' % mode_latency)
                fp.write('%d %.2f %.2f %.2f\n' % (clients, throughput, avg_latency, mode_latency))

                # graph the output for the single run of 4 clients
                if clients == 4: self.graph_four_clients(throughput, avg_latency, mode_latency)

        # plot the summary graph
        self.graph_all_clients()

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def run_client(self, name, network, num_iterations, start, out_dir, signal_file):
        pk = secrets.token_hex(32)
        account = Web3().eth.account.from_key(pk)
        self.distribute_native(account, Web3().from_wei(1, 'ether'))
        network.connect(self, private_key=pk, check_funds=False)

        if not os.path.exists(out_dir): os.mkdir(out_dir)
        stdout = os.path.join(out_dir, '%s.out' % name)
        stderr = os.path.join(out_dir, '%s.err' % name)
        script = os.path.join(self.input, 'client.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--num_iterations', '%d' % num_iterations])
        args.extend(['--client_name', name])
        args.extend(['--pk', pk])
        args.extend(['--start', '%d' % start])
        args.extend(['--signal_file', signal_file])
        self.run_python(script, stdout, stderr, args, workingDir=out_dir)
        self.waitForSignal(file=stdout, expr='Starting client %s' % name)

    def process_latency(self, num_clients, out_dir):
        data = []
        for i in range(0, num_clients):
            with open(os.path.join(out_dir, 'client_%s_latency.log' % i), 'r') as fp:
                for line in fp.readlines(): data.append(float(line.strip()))
        data.sort()
        avg_latency = (sum(data) / len(data))

        bins = self.bin_array(data)
        max_value = 0
        mode_latency = 0
        with open(os.path.join(out_dir, 'binned_latency.log'), 'w') as fp:
            for b,v in bins:
                if v > max_value:
                    max_value = v
                    mode_latency = b
                fp.write('%.2f %d\n' % (b, v))
            fp.flush()
        return avg_latency, mode_latency

    def process_throughput(self, num_clients, out_dir, start, end):
        client_bins = []       # bins for a given client
        bins = OrderedDict()   # total binned data across all clients
        for x in range(0, int((end-start)/1e9) + 1): bins[x] = 0
        for i in range(0, num_clients):
            client_times = []
            with open(os.path.join(out_dir, 'client_%s_throughput.log' % i), 'r') as fp:
                for line in fp.readlines():
                    time = math.floor(float(line.strip().split()[0]))
                    client_times.append(time)
                    bins[time] = bins[time]+1
                client_bins.append(client_times)

        # reduce to the overlap and find best zero gradient fit
        included = self.find_overlap(client_bins)
        bins_steady = {key: value for key, value in bins.items() if key in included}
        bins_ramp = {key: value for key, value in bins.items() if key not in included}
        throughput = self.find_best_fit(bins_steady)

        with open(os.path.join(out_dir, 'binned_throughput_all.log'), 'w') as fp:
            for t in bins.keys(): fp.write('%d %d\n' % (t, bins[t]))

        with open(os.path.join(out_dir, 'binned_throughput_steady.log'), 'w') as fp:
            for t in bins_steady.keys(): fp.write('%d %d %.2f\n' % (t, bins_steady[t], throughput))

        with open(os.path.join(out_dir, 'binned_throughput_ramp.log'), 'w') as fp:
            for t in bins_ramp.keys(): fp.write('%d %d\n' % (t, bins_ramp[t]))

        return throughput

    def graph_four_clients(self, throughput, avg_latency, mode_latency):
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        GnuplotHelper.graph(self, os.path.join(self.input, 'four_clients.in'), branch, date, str(self.mode),
                            '%.2f' % throughput, '%.2f' % avg_latency, '%.2f' % mode_latency)

    def graph_all_clients(self):
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        GnuplotHelper.graph(self, os.path.join(self.input, 'all_clients.in'), branch, date, str(self.mode))

    def bin_array(self, data, num_bins=40):
        min_val = min(data)
        max_val = max(data)
        bin_width = (max_val - min_val) / num_bins
        bin_counts = [0] * num_bins

        for val in data:
            bin_index = min(int((val - min_val) / bin_width), num_bins - 1)
            bin_counts[bin_index] += 1

        bins = []
        for i in range(num_bins):
            bin_start = min_val + i * bin_width
            bins.append((bin_start, bin_counts[i]))

        return bins

    def find_overlap(self, lists):
        if len(lists) == 0: return []
        overlap = np.array(lists[0])
        for l in lists[1:]: overlap = np.intersect1d(overlap, np.array(l))
        return overlap.tolist()[1:-1]

    def find_best_fit(self, data):
        x_values = np.array(np.array(list(data.keys())))
        y_values = np.array(np.array(list(data.values())))
        coeffs = np.polyfit(x_values, y_values, deg=0)
        best_fit_y_values = np.full_like(y_values, fill_value=coeffs[0])
        return best_fit_y_values[0]
