import os, secrets, shutil
from datetime import datetime
from collections import OrderedDict
from obscuro.test.contracts.error import Error
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.gnuplot import GnuplotHelper
from obscuro.test.helpers.wallet_extension import WalletExtension


class PySysTest(GenericNetworkTest):
    ITERATIONS = 5000
    ACCOUNTS = 20

    def execute(self):
        clients = ['one', 'two'] # need to manually change the gnuplot.in file for more clients

        # connect to the network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # we need to perform a transaction on the account to ensure the nonce is greater than zero for the
        # following bulk loading (a hack to avoid count=0 being considered a new deployment and clearing the db)
        error = Error(self, web3)
        error.deploy(network, account)

        # run the clients
        for i in clients: self.run_client('client_%s' % i, network)
        for i in clients:
            self.waitForGrep(file='client_%s.out' % i, expr='Client client_%s completed' % i, timeout=600)

        # process and graph the output
        data = [self.load_data('client_%s.log' % i) for i in clients]
        first = int(data[0][0][1])
        last = int(data[-1][-1][1])

        data_binned = [self.bin_data(first, last, d, OrderedDict()) for d in data]
        for i in clients:
            with open(os.path.join(self.output, 'client_%s.bin' % i), 'w') as fp:
                for key, value in data_binned[clients.index(i)].items(): fp.write('%d %d\n' % (key, value))

        with open(os.path.join(self.output, 'clients.bin'), 'w') as fp:
            for t in range(0, last + 1 - first):
                fp.write('%d %d\n' % (t, sum([d[t] for d in data_binned])))

        branch = GnuplotHelper.buildInfo().branch
        duration = last - first
        average = float(len(clients)*self.ITERATIONS) / float(duration) if duration != 0 else 0
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(len(clients)*self.ITERATIONS), str(duration), '%.3f' % average)

    def run_client(self, name, network, offset=2.0):
        """Run a background load client. """
        pk = secrets.token_hex(32)
        _, account = network.connect(self, private_key=pk)
        self.fund_obx(network, account, 10)

        http_port = self.getNextAvailableTCPPort()
        ws_port = self.getNextAvailableTCPPort()
        extension = WalletExtension(self, http_port, ws_port, name=name)
        extension.run()

        stdout = os.path.join(self.output, '%s.out' % name)
        stderr = os.path.join(self.output, '%s.err' % name)
        script = os.path.join(self.input, 'client.py')
        args = []
        args.extend(['--network_http', 'http://127.0.0.1:%d' % http_port])
        args.extend(['--chainId', '%s' % network.chain_id()])
        args.extend(['--pk', pk])
        args.extend(['--num_accounts', '%d' % self.ACCOUNTS])
        args.extend(['--num_iterations', '%d' % self.ITERATIONS])
        args.extend(['--client_name', name])
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting client %s' % name, timeout=10)
        self.wait(offset)

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

    def execute_graph(self):
        """Test method to develop graph creation. """
        shutil.copy(os.path.join(self.input, 'client_one.bin'), os.path.join(self.output, 'client_one.bin'))
        shutil.copy(os.path.join(self.input, 'client_two.bin'), os.path.join(self.output, 'client_two.bin'))
        shutil.copy(os.path.join(self.input, 'clients.bin'), os.path.join(self.output, 'clients.bin'))
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date, str(self.mode), str(2*self.ITERATIONS), '112', '89.286')


