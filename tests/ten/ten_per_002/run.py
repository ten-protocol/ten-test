import os, time
from datetime import datetime
from collections import OrderedDict
from pysys.constants import PASSED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 1024         # number of iterations per client
    ACCOUNTS = 8              # number of different accounts that receive the funds per client

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.gas_price = 0
        self.gas_limit = 0
        self.chain_id = 0
        self.value = 100
        self.clients = ['one', 'two']

    def execute(self):
        # connect to the network on the primary gateway and calculate funds needs
        network = self.get_network_connection(name='local' if self.is_local_ten() else 'primary', verbose=False)
        web3, _ = network.connect_account1(self)
        account = web3.eth.account.from_key(self.get_ephemeral_pk())
        self.chain_id = network.chain_id()
        self.gas_price = web3.eth.gas_price
        self.gas_limit = web3.eth.estimate_gas({'to': account.address, 'value': self.value, 'gasPrice': self.gas_price})
        funds_needed = 1.1 * self.ITERATIONS * (self.gas_price*self.gas_limit + self.value)

        # run the clients
        pk1, conn1 = self.setup_client('client_one', funds_needed)
        pk2, conn2 = self.setup_client('client_two', funds_needed)
        self.run_client('client_one', pk1, conn1)
        self.run_client('client_two', pk2, conn2)
        txs_sent = 0
        for i in self.clients:
            stdout = os.path.join(self.output,'client_%s.out' % i)
            self.waitForGrep(file=stdout, expr='Client client_%s completed' % i, timeout=900)
            self.assertGrep(file=stdout, expr='Error sending raw transaction', contains=False, abortOnError=False)
            txs_sent += self.txs_sent(file=stdout)

        # process and graph the output
        data = [self.load_data('client_%s.log' % i) for i in self.clients]
        first = int(data[0][0][1])
        last = int(data[-1][-1][1])

        data_binned = [self.bin_data(first, last, d, OrderedDict()) for d in data]
        for i in self.clients:
            with open(os.path.join(self.output, 'client_%s.bin' % i), 'w') as fp:
                for key, value in data_binned[self.clients.index(i)].items(): fp.write('%d %d\n' % (key, value))

        with open(os.path.join(self.output, 'clients.bin'), 'w') as fp:
            for t in range(0, last + 1 - first):
                fp.write('%d %d\n' % (t, sum([d[t] for d in data_binned])))

        branch = GnuplotHelper.buildInfo().branch
        duration = last - first
        average = float(txs_sent) / float(duration) if duration != 0 else 0
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(txs_sent), str(duration), '%.3f' % average)

        # persist the result
        if self.PERSIST_PERFORMANCE:
            self.results_db.insert_result(self.descriptor.id, self.mode, int(time.time()), average)

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def setup_client(self, name, funds_needed):
        pk = self.get_ephemeral_pk()
        network = self.get_network_connection(name='local' if self.is_local_ten() else 'primary', verbose=False)
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, web3.from_wei(funds_needed, 'ether'))
        return pk, network

    def run_client(self, name, pk, network):
        """Run a background load client. """
        stdout = os.path.join(self.output, '%s.out' % name)
        stderr = os.path.join(self.output, '%s.err' % name)
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
        self.run_python(script, stdout, stderr, args)
        self.waitForSignal(file=stdout, expr='Starting client %s' % name)

    def load_data(self, file):
        """Load a client transaction log into memory. """
        data = []
        with open(os.path.join(self.output, file), 'r') as fp:
            for line in fp.readlines():
                nonce, timestamp = line.split()
                data.append((nonce, int(timestamp)))
        return data

    def bin_data(self, first, last, data, binned_data):
        """Bin a client transaction data and offset the time. """
        b = OrderedDict()
        for _, t in data: b[t] = 1 if t not in b else b[t] + 1
        for t in range(first, last+1): binned_data[t-first] = 0 if t not in b else b[t]
        return binned_data
