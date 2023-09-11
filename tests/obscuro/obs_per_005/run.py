import secrets, os
from web3 import Web3
from obscuro.test.utils.timers import timeit
from obscuro.test.contracts.storage import Storage
from obscuro.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):
    ITERATIONS = 10
    CLIENTS = 5
    DURATION = 60

    @timeit
    def transact(self, network_connection, web3, storage, count, account):
        network_connection.transact(self, web3, storage.contract.functions.store(count), account, storage.GAS_LIMIT)

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.clients = []

    def execute(self):
        self.execute_graph()

    def execute_run(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 0)
        storage.deploy(network, account)

        # do a sanity check and break hard if the network is slow
        times = []
        for i in range(0, self.ITERATIONS):
            times.append(self.transact(network, web3, storage, 0, account))

        for i in range(0, self.CLIENTS):
            self.storage_client(storage.address, storage.abi_path, i, network)

        # run some concurrent clients to bin and plot the results
        for i in range(0, self.CLIENTS):
            self.waitForGrep(file='client_%d.out' % i, expr='Client running', timeout=10)

        self.wait(self.DURATION)
        self.log.info('Stopping all concurrent clients')
        for client in self.clients: client.stop()

    def storage_client(self, address, abi_path, num, network):
        pk = secrets.token_hex(32)
        account = Web3().eth.account.privateKeyToAccount(pk)
        self.distribute_native(account, 0.1)
        network.connect(self, private_key=pk)

        stdout = os.path.join(self.output, 'client_%d.out' % num)
        stderr = os.path.join(self.output, 'client_%d.err' % num)
        script = os.path.join(self.input, 'storage_client.py')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url()])
        args.extend(['--address', '%s' % address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--pk_to_register', '%s' % pk])
        args.extend(['--output_file', 'client_%s.log' % num])
        self.clients.append(self.run_python(script, stdout, stderr, args))

    def execute_graph(self):
        latencies = []
        for i in range(0, self.CLIENTS):
            with open(os.path.join(self.input, 'client_%d.log' % i), 'r') as fp:
                for line in fp.readlines():
                    latency = float(line.strip())
                    latencies.append(latency)
        latencies.sort()
        min = latencies[0]
        max = latencies[len(latencies)-1]
        bins = round(((max - min) / 10.0), 1)
        self.log.info('%.4f %.4f %.4f', min, max, bins)
