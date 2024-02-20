import os, math, time
from datetime import datetime
from collections import OrderedDict
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 512  # iterations per client, don't exceed bulk loading more than 1024
    CLIENTS = ['one', 'two']

    def execute(self):
        # connect to the network and determine constants and funds required to run the test
        network = self.get_network_connection()

        # run the clients and wait for their completion
        start = time.perf_counter()
        for i in self.CLIENTS: self.run_client('client_%s' % i, network, self.ITERATIONS)
        for i in self.CLIENTS:
            self.waitForGrep(file='client_%s.out' % i, expr='Client client_%s completed' % i,
                             timeout=900, poll=0.01)
        end = time.perf_counter()
        self.log.info('Duration of RPC request sending %d' % (end-start))

        # graph the output
        self.graph()

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def run_client(self, name, network, num_iterations=1000):
        """Run a background load client. """
        stdout = os.path.join(self.output, '%s.out' % name)
        stderr = os.path.join(self.output, '%s.err' % name)
        script = os.path.join(self.input, 'client.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--num_iterations', '%d' % num_iterations])
        args.extend(['--client_name', name])
        self.run_python(script, stdout, stderr, args)
        self.waitForSignal(file=stdout, expr='Client %s started' % name)

    def graph(self):
        # load the durations and sort
        l = []
        for i in self.CLIENTS:
            with open(os.path.join(self.output, 'client_%s.log' % i), 'r') as fp:
                for line in fp.readlines(): l.append(int(line.strip()))
        l.sort()
        self.log.info('Average duration = %.2f', (sum(l) / len(l)))
        self.log.info('Median duration = %.2f', l[int(len(l) / 2)])

        # bin into intervals and write to file
        bins = OrderedDict()
        bin_inc = 20
        bin = lambda x: int(math.floor(bin_inc*x))

        for i in range(bin(l[0]), bin(l[len(l)-1])+1): bins[i] = 0
        for v in l: bins[bin(v)] = bins[bin(v)] + 1
        with open(os.path.join(self.output, 'bins.log'), 'w') as fp:
            for k in bins.keys(): fp.write('%.2f %d\n' % (k/float(bin_inc), bins[k]))
            fp.flush()

        # plot out the results
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(len(l)), '%d' % len(self.CLIENTS), '%.2f' % (sum(l) / len(l)))

