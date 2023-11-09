import secrets, os
from web3 import Web3
from obscuro.test.helpers.ws_proxy import WebServerProxy
from obscuro.test.contracts.storage import KeyStorage
from obscuro.test.basetest import ObscuroNetworkTest


class PySysTest(ObscuroNetworkTest):
    ITERATIONS = 10
    CLIENTS = 5

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        contract = KeyStorage(self, web3)
        contract.deploy(network, account)

        self.client(network, contract, 'meaning_of_life', 42)
        value_after = contract.contract.functions.getItem('meaning_of_life').call()
        self.log.info('The meaning of life is ... %d', value_after)
        self.assertTrue(value_after == 42)

    def client(self, network, contract, key, value):
        private_key = secrets.token_hex(32)
        self.distribute_native(Web3().eth.account.privateKeyToAccount(private_key), 0.01)
        network.connect(self, private_key=private_key, check_funds=False)

        # create the client
        stdout = os.path.join(self.output, 'client.out')
        stderr = os.path.join(self.output, 'client.err')
        script = os.path.join(self.input, 'client.js')
        args = []
        args.extend(['--network', network.connection_url()])
        args.extend(['--address', contract.address])
        args.extend(['--contract_abi', contract.abi_path])
        args.extend(['--private_key', private_key])
        args.extend(['--key', key])
        args.extend(['--value', str(value)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting transactions', timeout=10)
        self.waitForGrep(file=stdout, expr='Completed transactions', timeout=40)



