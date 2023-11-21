import secrets, os, time, math
from web3 import Web3
from collections import OrderedDict
from datetime import datetime
from ten.test.contracts.storage import KeyStorage
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 10
    CLIENTS = 5
    DURATION = 120

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.clients = []

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        contract = KeyStorage(self, web3)
        contract.deploy(network, account)

        for i in range(0, self.CLIENTS): self.client(network, contract, i)
        for i in range(0, self.CLIENTS): self.waitForGrep(file='client_%d.out' % i, expr='Starting transactions', timeout=10)
        self.wait(self.DURATION)
        for client in self.clients: client.stop()
        self.graph()

    def client(self, network, contract, num):
        private_key = secrets.token_hex(32)
        account = Web3().eth.account.privateKeyToAccount(private_key)
        key = '%d_%d' % (int(time.time()), num)
        self.log.info('Client %d has key %s', num, key)
        self.distribute_native(account, 0.01)
        network.connect(self, private_key=private_key, check_funds=False)

        # create the client
        stdout = os.path.join(self.output, 'client_%d.out' % num)
        stderr = os.path.join(self.output, 'client_%d.err' % num)
        script = os.path.join(self.input, 'client.js')
        args = []
        args.extend(['--network', network.connection_url(web_socket=True)])
        args.extend(['--contract_address', contract.address])
        args.extend(['--contract_abi', contract.abi_path])
        args.extend(['--private_key', private_key])
        args.extend(['--key', key])
        args.extend(['--event_log', 'events_%s.log' % num])
        args.extend(['--receipt_log', 'receipts_%s.log' % num])
        self.clients.append(self.run_javascript(script, stdout, stderr, args))

    def graph(self):
        # load the latency values and sort
        l = []
        for i in range(0, self.CLIENTS):
            with open(os.path.join(self.output, 'events_%d.log' % i), 'r') as fp:
                for line in fp.readlines(): l.append(float(line.strip()))
        l.sort()
        self.log.info('Average latency = %.2f', (sum(l) / len(l)))
        self.log.info('Median latency = %.2f', l[int(len(l) / 2)])

        # bin into 0.1s intervals and write to file
        bins = OrderedDict()
        bin_inc = 20  # 0.05 intervals
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
                            str(self.mode), str(len(l)), str(self.DURATION), '%d' % self.CLIENTS)