import os, secrets
from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.guesser.guesser import Guesser
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.contracts.error.error import Error
from obscuro.test.networks.obscuro import Obscuro


class PySysTest(ObscuroNetworkTest):
    NUM_GUESSERS = 2
    NUM_STORAGE = 2
    NUM_ERROR = 2

    def execute(self):
        network = Obscuro
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        guesser = Guesser(self, web3, 0, 100)
        guesser.deploy(network, account)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        error = Error(self, web3, 'foo')
        error.deploy(network, account)

        #for i in range(0, self.NUM_GUESSERS):
        #    self.guesser_client(network, guesser.contract_address, guesser.abi_path, i)

        for i in range(0, self.NUM_STORAGE):
            self.storage_client(network, storage.contract_address, guesser.abi_path, i)

        #for i in range(0, self.NUM_ERROR):
        #    self.error_client(network, error.contract_address, guesser.abi_path, i)

        self.wait(20.0)

    def guesser_client(self, network, contract_address, abi_path, num):
        self._client(network, contract_address, abi_path, 'guesser_client', num)

    def storage_client(self, network, contract_address, abi_path, num):
        self._client(network, contract_address, abi_path, 'storage_client', num)

    def error_client(self, network, contract_address, abi_path, num):
        self._client(network, contract_address, abi_path, 'error_client', num)

    def _client(self, network, contract_address, abi_path, name, num):
        pk = secrets.token_hex(32)
        account = Web3().eth.account.privateKeyToAccount(pk)
        self.fund_obx(network, account, Web3().toWei(100, 'ether'))

        stdout = os.path.join(self.output, '%s_%d.out' % (name, num))
        stderr = os.path.join(self.output, '%s_%d.err' % (name, num))
        script = os.path.join(self.input, '%s.py' % name)
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--contract_address', '%s' % contract_address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--pk_to_register', '%s' % pk])
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Client running', timeout=10)