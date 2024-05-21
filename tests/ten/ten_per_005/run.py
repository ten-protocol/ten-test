import os, secrets, time, re
from datetime import datetime
from collections import OrderedDict
from pysys.constants import PASSED
from ten.test.contracts.storage import KeyStorage
from ten.test.basetest import TenNetworkTest
from ten.test.utils.gnuplot import GnuplotHelper


class PySysTest(TenNetworkTest):
    ITERATIONS = 2048      # iterations per client
    CLIENTS = 4            # the number of concurrent clients

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

        self.chain_id = network.chain_id()
        self.gas_price = web3.eth.gas_price
        params = {'from': account.address, 'chainId': web3.eth.chain_id, 'gasPrice': self.gas_price}
        self.gas_limit = storage.contract.functions.setItem('test', 1).estimate_gas(params)
        funds_needed = 1.1 * self.ITERATIONS * (self.gas_price*self.gas_limit)

        # run the clients
        setup = [self.setup_client('client_%d' % i, funds_needed) for i in range(self.CLIENTS)]
        for i in range(self.CLIENTS): self.run_client('client_%d' % i, storage, setup[i][0], setup[i][1])
        for i in range(self.CLIENTS):
            self.waitForGrep(file='client_%d.out' % i, expr='Client client_%d completed' % i, timeout=900)
            self.ratio_failures(file=os.path.join(self.output, 'client_%d.out' % i))

        # process and graph the output
        data = [self.load_data('client_%d.log' % i) for i in range(self.CLIENTS)]
        first = int(data[0][0][1])
        last = int(data[-1][-1][1])

        data_binned = [self.bin_data(first, last, d, OrderedDict()) for d in data]
        with open(os.path.join(self.output, 'clients_all.bin'), 'w') as fp:
            for t in range(0, last + 1 - first):
                fp.write('%d %s\n' % (t, ' '.join([str(d[t]) for d in data_binned])))

        heights = []
        with open(os.path.join(self.output, 'clients.bin'), 'w') as fp:
            for t in range(0, last + 1 - first):
                height = sum([d[t] for d in data_binned])
                heights.append(height)
                fp.write('%d %d\n' % (t, height))
                average = '%.2f' % (float(sum(heights)) / len(heights))

        # plot out the results
        branch = GnuplotHelper.buildInfo().branch
        duration = last - first
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(self.CLIENTS * self.ITERATIONS), str(duration), '%d' % self.CLIENTS)

        # persist the result
        self.results_db.insert_result(self.descriptor.id, self.mode, int(time.time()), average)

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def setup_client(self, name, funds_needed):
        pk = secrets.token_hex(32)
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, web3.from_wei(funds_needed, 'ether'))
        return pk, network

    def run_client(self, name, contract, pk, network):
        """Run a background load client. """
        stdout = os.path.join(self.output, '%s.out' % name)
        stderr = os.path.join(self.output, '%s.err' % name)
        script = os.path.join(self.input, 'storage_client.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--chainId', '%s' % network.chain_id()])
        args.extend(['--pk', pk])
        args.extend(['--contract_address', '%s' % contract.address])
        args.extend(['--contract_abi', '%s' % contract.abi_path])
        args.extend(['--num_iterations', '%d' % self.ITERATIONS])
        args.extend(['--client_name', name])
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
        for t in range(first, last + 1): binned_data[t - first] = 0 if t not in b else b[t]
        return binned_data

    def ratio_failures(self, file):
        ratio = None
        regex = re.compile('Ratio failures = (?P<ratio>.*)$', re.M)
        with open(file, 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None:
                    ratio = float(result.group('ratio'))
        self.log.info('Ratio of failures is %.2f' % ratio)
        return ratio