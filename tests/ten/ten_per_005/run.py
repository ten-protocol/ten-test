import os, time
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
        network = self.get_network_connection(name='local' if self.is_local_ten() else 'primary', verbose=False)
        web3, account = network.connect_account1(self)
        storage = KeyStorage(self, web3)
        storage.deploy(network, account)

        self.chain_id = network.chain_id()
        self.gas_price = web3.eth.gas_price
        params = {'from': account.address, 'chainId': web3.eth.chain_id, 'gasPrice': self.gas_price}
        self.gas_limit = 4*storage.contract.functions.setItem('test', 1).estimate_gas(params)
        funds_needed = 1.1 * self.ITERATIONS * (self.gas_price*self.gas_limit)

        # run the clients
        setup = [self.setup_client('client_%d' % i, funds_needed) for i in range(self.CLIENTS)]
        for i in range(self.CLIENTS): self.run_client('client_%d' % i, storage, setup[i][0], setup[i][1])
        txs_sent = 0
        for i in range(self.CLIENTS):
            stdout = os.path.join(self.output,'client_%d.out' % i)
            self.waitForGrep(file=stdout, expr='Client client_%d completed' % i, timeout=900)
            self.assertGrep(file=stdout, expr='Error sending raw transaction', contains=False, abortOnError=False)
            txs_sent += self.txs_sent(file=stdout)

        # process (data is an array of each client results - each is an array of tuple (nonce, ts, block height))
        data = [self.load_data('client_%d.log' % i) for i in range(self.CLIENTS)]

        # bin based on timestamps (both for each client, and across all clients)
        first_ts = int(data[0][0][1])   # first client, first data, ts
        last_ts = int(data[-1][-1][1])  # last client, last data, ts
        duration = last_ts - first_ts
        data_binned_ts = [self.bin_timestamp_data(first_ts, last_ts, d, OrderedDict()) for d in data]
        with open(os.path.join(self.output, 'clients_all_ts.bin'), 'w') as fp:
            for t in range(0, last_ts + 1 - first_ts):
                fp.write('%d %s\n' % (t, ' '.join([str(d[t]) for d in data_binned_ts])))

        with open(os.path.join(self.output, 'clients_ts.bin'), 'w') as fp:
            for t in range(0, last_ts + 1 - first_ts):
                height = sum([d[t] for d in data_binned_ts])
                fp.write('%d %d\n' % (t, height))

        # bin based on block height (across all clients)
        first_bh = int(data[0][0][2])   # first client, first data, block height
        last_bh = int(data[-1][-1][2])  # last client, last data, block height
        data_binned_bh = [self.bin_block_height_data(first_bh, last_bh, d, OrderedDict()) for d in data]
        with open(os.path.join(self.output, 'clients_bh.bin'), 'w') as fp:
            for t in range(0, last_bh + 1 - first_bh):
                height = sum([d[t] for d in data_binned_bh])
                fp.write('%d %d\n' % (t, height))

        # plot out the results
        branch = GnuplotHelper.buildInfo().branch
        date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        GnuplotHelper.graph(self, os.path.join(self.input, 'gnuplot.in'),
                            branch, date,
                            str(self.mode), str(txs_sent), str(duration), '%d' % self.CLIENTS)

        # persist the result
        if self.PERSIST_PERF:
            self.results_db.insert_result(self.descriptor.id, self.mode, int(time.time()), float(txs_sent)/float(duration))

        # passed if no failures (though pdf output should be reviewed manually)
        self.addOutcome(PASSED)

    def setup_client(self, name, funds_needed):
        pk = self.get_ephemeral_pk()
        network = self.get_network_connection(name='local' if self.is_local_ten() else 'primary', verbose=False)
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
                nonce, timestamp, block_num = line.split()
                data.append((nonce, int(timestamp), int(block_num)))
        return data

    @staticmethod
    def bin_timestamp_data(first, last, data, binned_data):
        """Bin a client transaction data or timestamp, and offset. """
        b = OrderedDict()
        for _, t, _ in data: b[t] = 1 if t not in b else b[t] + 1
        for t in range(first, last + 1): binned_data[t - first] = 0 if t not in b else b[t]
        return binned_data

    @staticmethod
    def bin_block_height_data(first, last, data, binned_data):
        """Bin a client transaction data for block height, and offset."""
        b = OrderedDict()
        for _, _, h in data: b[h] = 1 if h not in b else b[h] + 1
        for h in range(first, last + 1): binned_data[h - first] = 0 if h not in b else b[h]
        return binned_data