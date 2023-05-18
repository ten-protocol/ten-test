import os, secrets
from web3 import Web3
from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.guesser import Guesser
from obscuro.test.contracts.storage import Storage
from obscuro.test.contracts.error import Error
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.helpers.wallet_extension import WalletExtension
from obscuro.test.utils.properties import Properties


class PySysTest(ObscuroNetworkTest):
    NUM_FUNDS = 5
    NUM_GUESSERS = 4
    NUM_STORAGE = 4
    NUM_ERROR = 2
    DURATION = 120

    def __init__(self, descriptor, outsubdir, runner):
        super().__init__(descriptor, outsubdir, runner)
        self.clients = []

    def execute(self):
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # set up the wallets and deploy contracts
        funders = [secrets.token_hex() for _ in range(0, self.NUM_FUNDS)]

        guesser = Guesser(self, web3, 0, 100)
        guesser.deploy(network, account)
        guesser_wallet = WalletExtension.start(self, name='guesser')

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        storage_wallet = WalletExtension.start(self, name='storage')

        error = Error(self, web3)
        error.deploy(network, account)
        error_wallet = WalletExtension.start(self, name='error')

        # create the clients
        for i in range(0, len(funders)):
            recipients = [Web3().eth.account.privateKeyToAccount(x).address for x in funders if x != funders[i]]
            self.funds_client(network, funders[i], recipients, i)

        for i in range(0, self.NUM_GUESSERS):
            self.guesser_client(network, guesser.address, guesser.abi_path, i, guesser_wallet)

        for i in range(0, self.NUM_STORAGE):
            self.storage_client(network, storage.address, storage.abi_path, i, storage_wallet)

        for i in range(0, self.NUM_ERROR):
            self.error_client(network, error.address, error.abi_path, i, error_wallet)

        # wait the duration of the test, then check we can still transact
        self.wait(self.DURATION)
        self.log.info('Stopping all concurrent clients')
        for client in self.clients: client.stop()
        self.wait(2.0*float(self.block_time))

        self.log.info('Transact and check')
        network.transact(self, web3, storage.contract.functions.store(1812), account, storage.GAS_LIMIT)
        self.wait(2.0*float(self.block_time))
        value = storage.contract.functions.retrieve().call()
        self.log.info('Call shows value %d' % storage.contract.functions.retrieve().call())
        self.assertTrue(value == 1812)

    def funds_client(self, network, pk, recipients, num):
        wallet = WalletExtension.start(self, name='funds_%d' % num)
        self.fund_native(network, Web3().eth.account.privateKeyToAccount(pk), 1, Properties().funded_account_pk(self))

        stdout = os.path.join(self.output, 'funds_%d.out' % num)
        stderr = os.path.join(self.output, 'funds_%d.err' % num)
        script = os.path.join(self.input, 'funds_client.py')
        args = []
        args.extend(['--network_http', '%s' % wallet.connection_url()])
        args.extend(['--pk_to_register', '%s' % pk])
        args.extend(['--recipients', ','.join([str(i) for i in recipients])])
        self.clients.append(self.run_python(script, stdout, stderr, args))
        self.waitForGrep(file=stdout, expr='Client running', timeout=10)

    def guesser_client(self, network, address, abi_path, num, wallet):
        self._client(network, address, abi_path, 'guesser_client', num, wallet)

    def storage_client(self, network, address, abi_path, num, wallet):
        self._client(network, address, abi_path, 'storage_client', num, wallet)

    def error_client(self, network, address, abi_path, num, wallet):
        self._client(network, address, abi_path, 'error_client', num, wallet)

    def _client(self, network, address, abi_path, name, num, wallet):
        pk = secrets.token_hex(32)
        account = Web3().eth.account.privateKeyToAccount(pk)
        self.fund_native(network, account, 1, Properties().funded_account_pk(self))

        stdout = os.path.join(self.output, '%s_%d.out' % (name, num))
        stderr = os.path.join(self.output, '%s_%d.err' % (name, num))
        script = os.path.join(self.input, '%s.py' % name)
        args = []
        args.extend(['--network_http', '%s' % wallet.connection_url(web_socket=False)])
        args.extend(['--address', '%s' % address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--pk_to_register', '%s' % pk])
        self.clients.append(self.run_python(script, stdout, stderr, args))
        self.waitForGrep(file=stdout, expr='Client running', timeout=10)