import os
from web3 import Web3
from pysys.constants import PROJECT
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.guesser import Guesser
from ten.test.contracts.storage import Storage
from ten.test.contracts.error import Error


class PySysTest(TenNetworkTest):
    NUM_FUNDS = 5
    NUM_STORAGE = 2
    NUM_STORAGE_SK = 2
    NUM_GUESSERS = 4
    NUM_ERROR = 2
    DURATION = 60

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.clients = []
        self.client_connections = []

    def execute(self):
        # connect to the network on the primary gateway
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contracts and create a new connection on the primary gateway for each client
        funders = [self.get_ephemeral_pk() for _ in range(0, self.NUM_FUNDS)]
        funders_connection = self.get_network_connection()

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        storage_connection = self.get_network_connection()

        guesser = Guesser(self, web3, 0, 100)
        guesser.deploy(network, account)
        guesser_connection = self.get_network_connection()

        error = Error(self, web3)
        error.deploy(network, account)
        error_connection = self.get_network_connection()

        # create the clients and get them running concurrently
        for i in range(0, len(funders)):
            recipients = [Web3().eth.account.from_key(x).address for x in funders if x != funders[i]]
            self.funds_client(network, funders[i], recipients, i, funders_connection)

        for i in range(0, self.NUM_STORAGE):
            self.storage_client(storage.address, storage.abi_path, i, storage_connection)

        for i in range(0, self.NUM_STORAGE_SK):
            self.storage_client_sk(storage.address, storage.abi_path, i)

        for i in range(0, self.NUM_GUESSERS):
            self.guesser_client(guesser.address, guesser.abi_path, i, guesser_connection)

        for i in range(0, self.NUM_ERROR):
            self.error_client(error.address, error.abi_path, i, error_connection)

        # wait the duration of the test, then check we can still transact
        self.wait(self.DURATION)
        self._stop_clients()
        self.wait(2.0*float(self.block_time))

        self.log.info('Transact and check')
        network.transact(self, web3, storage.contract.functions.store(1812), account, storage.GAS_LIMIT, timeout=300)
        self.wait(2.0*float(self.block_time))
        value = storage.contract.functions.retrieve().call()
        self.log.info('Call shows value %d', storage.contract.functions.retrieve().call())
        self.assertTrue(value == 1812)

    def funds_client(self, network, pk, recipients, num, funders_connection):
        web3, account = funders_connection.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, 5*network.ETH_ALLOC_EPHEMERAL)

        stdout = os.path.join(self.output, 'funds_%d.out' % num)
        stderr = os.path.join(self.output, 'funds_%d.err' % num)
        script = os.path.join(PROJECT.root, 'src', 'python', 'scripts', 'funds_client.py')
        args = []
        args.extend(['--network_http', '%s' % funders_connection.connection_url()])
        args.extend(['--pk_to_register', '%s' % pk])
        args.extend(['--recipients', ','.join([str(i) for i in recipients])])
        self.clients.append(self.run_python(script, stdout, stderr, args))
        self.waitForGrep(file=stdout, expr='Client running', timeout=10)

    def storage_client(self, address, abi_path, num, network):
        self._client(address, abi_path, 'storage_client', num, network)

    def storage_client_sk(self, address, abi_path, num):
        network = self.get_network_connection()
        web3, account = network.connect(self, private_key=self.get_ephemeral_pk(), check_funds=False)
        self.distribute_native(account, 5*network.ETH_ALLOC_EPHEMERAL)
        sk = self.get_session_key(network.connection_url())
        tx = {'to': sk, 'value': web3.to_wei(0.9*5*network.ETH_ALLOC_EPHEMERAL, 'ether'), 'gasPrice': web3.eth.gas_price, 'chainId': web3.eth.chain_id}
        tx['gas'] = web3.eth.estimate_gas(tx)
        network.tx(self, web3, tx, account)

        stdout = os.path.join(self.output, 'storage_client_sk_%d.out' % num)
        stderr = os.path.join(self.output, 'storage_client_sk_%d.err' % num)
        script = os.path.join(self.input, 'storage_client_sk.py')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url()])
        args.extend(['--address', '%s' % address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--session_key', '%s' % sk])
        self.clients.append(self.run_python(script, stdout, stderr, args))
        self.waitForGrep(file=stdout, expr='Client running', timeout=10)

    def guesser_client(self, address, abi_path, num, network):
        self._client(address, abi_path, 'guesser_client', num, network, False)

    def error_client(self, address, abi_path, num, network):
        self._client(address, abi_path, 'error_client', num, network, False)

    def _client(self, address, abi_path, name, num, network, fund=True):
        pk = self.get_ephemeral_pk()
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        if fund:
            self.distribute_native(account, 5*network.ETH_ALLOC_EPHEMERAL)
            self.client_connections.append((web3, account, network))

        stdout = os.path.join(self.output, '%s_%d.out' % (name, num))
        stderr = os.path.join(self.output, '%s_%d.err' % (name, num))
        script = os.path.join(self.input, '%s.py' % name)
        args = []
        args.extend(['--network_http', '%s' % network.connection_url()])
        args.extend(['--address', '%s' % address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--pk_to_register', '%s' % pk])
        self.clients.append(self.run_python(script, stdout, stderr, args))
        self.waitForGrep(file=stdout, expr='Client running', timeout=10)

    def _stop_clients(self):
        self.log.info('Stopping all concurrent clients')
        for client in self.clients: client.stop()
