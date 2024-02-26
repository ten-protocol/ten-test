import os, time, secrets
from web3 import Web3
from datetime import datetime
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 1024  # iterations per client, don't exceed bulk loading more than 1024

    def execute(self):
        # connect to the network and determine constants and funds required to run the test
        network = self.get_network_connection()

        # run the clients and wait for their completion
        for clients in [2, 4, 6]:
            self.log.info(' ')
            self.log.info('Running for %d clients' % clients)
            out_dir = os.path.join(self.output, 'clients_%d' % clients)
            start_ns = time.perf_counter_ns()
            for i in range(0, clients):
                self.run_client('client_%s' % i, network, self.ITERATIONS, start_ns, out_dir)
            for i in range(0, clients):
                self.waitForGrep(file=os.path.join(out_dir, 'client_%s.out' % i),
                                 expr='Client client_%s completed' % i, timeout=900)
            end_ns = time.perf_counter_ns()
            throughput = float(clients * self.ITERATIONS) / float((end_ns-start_ns)/1e9)
            self.log.info('Bulk rate throughput %.2f (requests/sec)' % throughput)

            # graph the output for the single run of 4 clients
            if clients == 4: self.graph_single_run(num_clients=4, out_dir=out_dir, throughput=throughput)

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def run_client(self, name, network, num_iterations, start, out_dir):
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
        self.run_python(script, stdout, stderr, args, workingDir=out_dir)

    def graph_single_run(self, num_clients, out_dir, throughput):
        data = []
        for i in range(0, num_clients):
            with open(os.path.join(out_dir, 'client_%s_latency.log' % i), 'r') as fp:
                for line in fp.readlines(): data.append(float(line.strip()))
        data.sort()
        avg_latency = (sum(data) / len(data))

        bins = self.bin_array(data)
        max_value = 0
        mode_latency = 0
        with open(os.path.join(out_dir, 'bins.log'), 'w') as fp:
            for b,v in bins:
                if v > max_value:
                    max_value = v
                    mode_latency = b
                fp.write('%.2f %d\n' % (b, v))
            fp.flush()

        # plot out the results
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        GnuplotHelper.graph(self, os.path.join(self.input, 'single_run.in'), branch, date, str(self.mode),
                            '%.2f' % throughput, '%.2f' % avg_latency, '%.2f' % mode_latency)

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