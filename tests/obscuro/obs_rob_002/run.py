import os, secrets
from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.guesser.guesser import Guesser
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.contracts.error.error import Error
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.helpers.wallet_extension import WalletExtension


class PySysTest(ObscuroNetworkTest):
    NUM_GUESSERS = 4
    NUM_STORAGE = 4
    NUM_ERROR = 2
    DURATION = 120

    def execute(self):
        network = Obscuro
        web3, account = network.connect_account1(self)

        guesser = Guesser(self, web3, 0, 100)
        guesser.deploy(network, account)
        guesser_wallet = WalletExtension(self, name='guesser')
        guesser_wallet.run()

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        storage_wallet = WalletExtension(self, name='storage')
        storage_wallet.run()

        error = Error(self, web3, 'foo')
        error.deploy(network, account)
        error_wallet = WalletExtension(self, name='error')
        error_wallet.run()

        self.clients = []
        for i in range(0, self.NUM_GUESSERS):
            self.guesser_client(network, guesser.contract_address, guesser.abi_path, i, guesser_wallet)

        for i in range(0, self.NUM_STORAGE):
            self.storage_client(network, storage.contract_address, storage.abi_path, i, storage_wallet)

        for i in range(0, self.NUM_ERROR):
            self.error_client(network, error.contract_address, error.abi_path, i, error_wallet)

        self.wait(self.DURATION)
        self.log.info('Stopping all concurrent clients')
        for client in self.clients: client.stop()

        self.log.info('Waiting 2 block periods')
        self.wait(2.0*float(self.block_time))

        self.log.info('Transact and check')
        network.transact(self, web3, storage.contract.functions.store(1812), account, storage.GAS_LIMIT)
        value = storage.contract.functions.retrieve().call()
        self.log.info('Call shows value %d' % storage.contract.functions.retrieve().call())
        self.assertTrue(value == 1812)

    def guesser_client(self, network, contract_address, abi_path, num, wallet):
        self._client(network, contract_address, abi_path, 'guesser_client', num, wallet)

    def storage_client(self, network, contract_address, abi_path, num, wallet):
        self._client(network, contract_address, abi_path, 'storage_client', num, wallet)

    def error_client(self, network, contract_address, abi_path, num, wallet):
        self._client(network, contract_address, abi_path, 'error_client', num, wallet)

    def _client(self, network, contract_address, abi_path, name, num, wallet):
        pk = secrets.token_hex(32)
        account = Web3().eth.account.privateKeyToAccount(pk)
        self.fund_obx(network, account, Web3().toWei(100, 'ether'))

        stdout = os.path.join(self.output, '%s_%d.out' % (name, num))
        stderr = os.path.join(self.output, '%s_%d.err' % (name, num))
        script = os.path.join(self.input, '%s.py' % name)
        args = []
        args.extend(['--network_http', '%s' % wallet.connection_url(web_socket=False)])
        args.extend(['--contract_address', '%s' % contract_address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--pk_to_register', '%s' % pk])
        self.clients.append(self.run_python(script, stdout, stderr, args))
        self.waitForGrep(file=stdout, expr='Client running', timeout=10)