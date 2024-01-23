import os, secrets, shutil
from datetime import datetime
from collections import OrderedDict
from ten.test.contracts.error import Error
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 512        # don't exceed bulk loading more than 1024 (2 clients used)
    SENDING_ACCOUNTS = 20
    RECEIVING_ACCOUNTS = 20

    def execute(self):
        self.execute_run()

    def execute_run(self):
        clients = ['one', 'two']  # need to manually change the gnuplot.in file for more clients

        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # we need to perform a transaction on the account to ensure the nonce is greater than zero for the
        # following bulk loading (a hack to avoid count=0 being considered a new deployment and clearing the db)
        error = Error(self, web3)
        error.deploy(network, account)

        # run the clients
        pk_file1, conn1 = self.setup_client('client_one')
        pk_file2, conn2 = self.setup_client('client_two')
        self.run_client('client_one', pk_file1, conn1)
        self.run_client('client_two', pk_file2, conn2)
        for i in clients:
            self.waitForGrep(file='client_%s.out' % i, expr='Client client_%s completed' % i, timeout=900)

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
        average = float(len(clients) * self.ITERATIONS) / float(duration) if duration != 0 else 0
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(len(clients) * self.ITERATIONS), str(duration), '%.3f' % average)

    def setup_client(self, name):
        pk_file = '%s_pk.txt' % name
        network = self.get_network_connection(name=name)
        with open(os.path.join(self.output, pk_file), 'w') as fw:
            for i in range(0, self.SENDING_ACCOUNTS):
                pk = secrets.token_hex(32)
                _, account = network.connect(self, private_key=pk, check_funds=False)
                self.distribute_native(account, 0.01)
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
        self.run_python(script, stdout, stderr, args)
        self.wait(1.0)

    def load_data(self, file):
        """Load a client transaction log into memory. """
        data = []
        with open(os.path.join(self.output, file), 'r') as fp:
            for line in fp.readlines():
                nonce, block_nume, timestamp = line.split()
                data.append((nonce, int(timestamp)))
        return data

    def bin_data(self, first, last, data, binned_data):
        """Bin a client transaction data and offset the time. """
        b = OrderedDict()
        for _, t in data: b[t] = 1 if t not in b else b[t] + 1
        for t in range(first, last + 1): binned_data[t - first] = 0 if t not in b else b[t]
        return binned_data

    def execute_graph(self):
        """Test method to develop graph creation. """
        shutil.copy(os.path.join(self.input, 'client_one.bin'), os.path.join(self.output, 'client_one.bin'))
        shutil.copy(os.path.join(self.input, 'client_two.bin'), os.path.join(self.output, 'client_two.bin'))
        shutil.copy(os.path.join(self.input, 'clients.bin'), os.path.join(self.output, 'clients.bin'))
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date, str(self.mode), str(2 * self.ITERATIONS), '51', '196.078')
