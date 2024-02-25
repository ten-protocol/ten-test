import os, time, secrets
from web3 import Web3
from datetime import datetime
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 1024  # iterations per client, don't exceed bulk loading more than 1024
    CLIENTS = 4

    def execute(self):
        # connect to the network and determine constants and funds required to run the test
        network = self.get_network_connection()

        # run the clients and wait for their completion
        start = time.perf_counter()
        start_ns = time.perf_counter_ns()
        for i in range(0, self.CLIENTS):
            self.run_client('client_%s' % i, network, self.ITERATIONS, start_ns)
        for i in range(0, self.CLIENTS):
            self.waitForGrep(file='client_%s.out' % i, expr='Client client_%s completed' % i,
                             timeout=900)
        end = time.perf_counter()

        duration = (end-start)
        total_sent = self.CLIENTS * self.ITERATIONS
        self.log.info('Duration of RPC request sending %.4f' % duration)
        self.log.info('Bulk rate throughput %d (requests/sec)' % (total_sent / duration))

        # graph the output
        self.graph()

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def run_client(self, name, network, num_iterations, start):
        """Run a background load client. """
        pk = secrets.token_hex(32)
        account = Web3().eth.account.from_key(pk)
        self.distribute_native(account, Web3().from_wei(1, 'ether'))
        network.connect(self, private_key=pk, check_funds=False)

        stdout = os.path.join(self.output, '%s.out' % name)
        stderr = os.path.join(self.output, '%s.err' % name)
        script = os.path.join(self.input, 'client.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--num_iterations', '%d' % num_iterations])
        args.extend(['--client_name', name])
        args.extend(['--pk', pk])
        args.extend(['--start', '%d' % start])
        self.run_python(script, stdout, stderr, args)

    def graph(self):
        # load the durations and sort
        data = []
        for i in range(0, self.CLIENTS):
            with open(os.path.join(self.output, 'client_%s_latency.log' % i), 'r') as fp:
                for line in fp.readlines(): data.append(float(line.strip()))
        data.sort()
        self.log.info('Average latency per client %f (ms)', (sum(data) / len(data)))
        self.log.info('Median latency per client %f (ms)', data[int(len(data) / 2)])

        bins = self.bin_array(data)
        with open(os.path.join(self.output, 'bins.log'), 'w') as fp:
            for b,v in bins: fp.write('%.2f %d\n' % (b, v))
            fp.flush()

        # plot out the results
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(len(data)), '%d' % self.CLIENTS, '%.2f' % (sum(data) / len(data)))

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