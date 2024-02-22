import secrets, os, math, time
from datetime import datetime
from collections import OrderedDict
from web3 import Web3
from pysys.constants import FAILED, PASSED
from ten.test.contracts.storage import Storage
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS_SANITY = 10      # initial set of checks on the latency before the concurrent clients
    ITERATIONS_FULL = 128       # total number of iterations per concurrent client
    CLIENTS = 5                 # the number of concurrent clients

    def transact(self, network_connection, web3, storage, count, account, gas_limit):
        start_time = time.perf_counter()
        network_connection.transact(self, web3, storage.contract.functions.store(count), account, gas_limit)
        end_time = time.perf_counter()
        return end_time - start_time

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.gas_price = 0
        self.gas_limit = 0
        self.chain_id = 0

    def execute(self):
        # connect to the network on the primary gateway and deploy the contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        self.chain_id = network.chain_id()
        self.gas_price = web3.eth.gas_price
        params = {'from': account.address, 'chainId': web3.eth.chain_id, 'gasPrice': self.gas_price}
        self.gas_limit = storage.contract.functions.store(1).estimate_gas(params)
        funds_needed = 1.1 * self.ITERATIONS_FULL * (self.gas_price*self.gas_limit)

        # do a sanity check and break hard if the network is slow
        times = []
        for i in range(0, self.ITERATIONS_SANITY):
            times.append(self.transact(network, web3, storage, 0, account, self.gas_limit))
        avg = (sum(times) / len(times))
        self.log.info('Average latency for %d transactions is %.2f', self.ITERATIONS_SANITY, avg)
        if avg > 10.0: self.addOutcome(FAILED, outcomeReason='Average latency %.2f is greater than 10 seconds' % avg)

        # run some concurrent clients, bin the latency and plot the results
        if self.ITERATIONS_FULL > 0:
            self.log.info('')
            self.log.info('Starting all concurrent clients')
            for i in range(0, self.CLIENTS):
                self.storage_client(storage.address, storage.abi_path, i, network, funds_needed)
            for i in range(0, self.CLIENTS):
                self.waitForGrep(file='client_%d.out' % i, expr='Client completed', timeout=300)
            self.graph()

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def storage_client(self, address, abi_path, num, network, funds_needed):
        pk = secrets.token_hex(32)
        account = Web3().eth.account.from_key(pk)
        self.distribute_native(account, Web3().from_wei(funds_needed, 'ether'))
        network.connect(self, private_key=pk, check_funds=False)

        stdout = os.path.join(self.output, 'client_%d.out' % num)
        stderr = os.path.join(self.output, 'client_%d.err' % num)
        script = os.path.join(self.input, 'storage_client.py')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url()])
        args.extend(['--address', '%s' % address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--pk_to_register', '%s' % pk])
        args.extend(['--output_file', 'client_%s.log' % num])
        args.extend(['--gas_limit', '%d' % self.gas_limit])
        args.extend(['--num_iterations', '%d' % self.ITERATIONS_FULL])
        self.run_python(script, stdout, stderr, args)

    def graph(self):
        # load the latency values and sort
        l = []
        for i in range(0, self.CLIENTS):
            with open(os.path.join(self.output, 'client_%d.log' % i), 'r') as fp:
                for line in fp.readlines(): l.append(float(line.strip()))
        l.sort()
        self.log.info('Average latency = %.2f', (sum(l) / len(l)))
        self.log.info('Median latency = %.2f', l[int(len(l) / 2)])

        # bin into intervals and write to file
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
                            str(self.mode), str(len(l)), '%d' % self.CLIENTS, '%.2f' % (sum(l) / len(l)))
