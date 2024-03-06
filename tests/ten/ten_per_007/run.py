import secrets, os, time, math
from web3 import Web3
from collections import OrderedDict
from datetime import datetime
from pysys.constants import PASSED
from ten.test.contracts.storage import KeyStorage
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 256          # total number of iterations per concurrent client
    CLIENTS = 5               # the number of concurrent clients

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.gas_price = 0
        self.gas_limit = 0
        self.chain_id = 0

    def execute(self):
        # connect to the network on the primary gateway and deploy the contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)
        storage = KeyStorage(self, web3)
        storage.deploy(network, account)

        # estimate funds and start the clients
        self.chain_id = network.chain_id()
        self.gas_price = web3.eth.gas_price
        params = {'from': account.address, 'chainId': web3.eth.chain_id, 'gasPrice': self.gas_price}
        self.gas_limit = storage.contract.functions.setItem("one", 1).estimate_gas(params)
        funds_needed = 1.1 * self.ITERATIONS * (self.gas_price*self.gas_limit)

        for i in range(0, self.CLIENTS):
            self.client(network, storage, i, funds_needed)

        for i in range(0, self.CLIENTS):
            self.waitForGrep(file='client_%d.out' % i, expr='Completed transactions', timeout=450)

        # graph the output
        self.graph()

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def client(self, network, contract, num, funds_needed):
        private_key = secrets.token_hex(32)
        account = Web3().eth.account.from_key(private_key)
        key = '%d_%d' % (int(time.time()), num)
        self.log.info('Client %d has key %s', num, key)
        self.distribute_native(account, Web3().from_wei(funds_needed, 'ether'))
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
        args.extend(['--output_file', 'client_%d.log' % num])
        args.extend(['--num_iterations', '%d' % self.ITERATIONS])
        self.run_javascript(script, stdout, stderr, args)

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

