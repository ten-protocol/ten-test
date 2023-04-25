import os, shutil, secrets
from datetime import datetime
from obscuro.test.contracts.error import Error
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.gnuplot import GnuplotHelper
from obscuro.test.helpers.wallet_extension import WalletExtension


class PySysTest(GenericNetworkTest):
    ITERATIONS = 2500
    CLIENTS = 1
    ACCOUNTS = 20

    def execute(self):
        self.execute_run()

    def execute_run(self):
        # connect to the network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # we need to perform a transaction on the account to ensure the nonce is greater than zero for the
        # following bulk loading (a hack to avoid count=0 being considered a new deployment and clearing the db)
        error = Error(self, web3)
        error.deploy(network, account)

        # run a client
        for i in ['one', 'two']:
            self.run_client(i, network)
            self.wait(5.0)

        for i in ['one', 'two']:
            self.waitForGrep(file='client_%s.out'%i, expr='Client %s completed'%i, timeout=600)

        # graph the output
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'), branch, date,
                            str(self.mode), str(self.ITERATIONS))

    def run_client(self, name, network):
        """Run a background load client. """
        pk = secrets.token_hex(32)
        _, account = network.connect(self, private_key=pk)
        self.fund_obx(network, account, 10)

        http_port = self.getNextAvailableTCPPort()
        ws_port = self.getNextAvailableTCPPort()
        extension = WalletExtension(self, http_port, ws_port, name=name)
        extension.run()

        stdout = os.path.join(self.output, 'client_%s.out' % name)
        stderr = os.path.join(self.output, 'client_%s.err' % name)
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

    def execute_graph(self):
        """Test method to develop graph creation. """
        branch = GnuplotHelper.buildInfo().branch
        duration = 93
        average = 53.1234
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        shutil.copy(os.path.join(self.input, 'data_one.bin'), os.path.join(self.output, 'data.bin'))
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(self.ITERATIONS), str(duration), '%.3f' % average)
