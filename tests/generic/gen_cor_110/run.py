import secrets, os
from web3 import Web3
from ten.test.contracts.storage import KeyStorage, Storage
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):
    ITERATIONS = 10
    CLIENTS = 5

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        key_storage = KeyStorage(self, web3)
        key_storage.deploy(network, account)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        self.client(network, storage.address, key_storage.abi_path, 'key', 42)

    def client(self, network, address, abi_path, key, value):
        private_key = secrets.token_hex(32)
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC_EPHEMERAL)
        network.connect(self, private_key=private_key, check_funds=False)

        # create the client
        stdout = os.path.join(self.output, 'client.out')
        stderr = os.path.join(self.output, 'client.err')
        logout = os.path.join(self.output, 'client.log')
        script = os.path.join(self.input, 'client.js')
        args = []
        args.extend(['--network', network.connection_url()])
        args.extend(['--address', address])
        args.extend(['--contract_abi', abi_path])
        args.extend(['--private_key', private_key])
        args.extend(['--key', key])
        args.extend(['--value', str(value)])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting transactions', timeout=10)
        self.waitForGrep(file=stderr, expr="code: \'CALL_EXCEPTION\'", timeout=10)

        # add an explicit assert on the call exception
        self.assertGrep(file=stderr, expr="code: \'CALL_EXCEPTION\'")


