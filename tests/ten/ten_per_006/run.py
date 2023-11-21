import secrets, os, time
from web3 import Web3
from ten.test.contracts.storage import KeyStorage
from ten.test.basetest import TenNetworkTest


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
        args.extend(['--output_file', 'client_%s.log' % num])
        self.clients.append(self.run_javascript(script, stdout, stderr, args))
