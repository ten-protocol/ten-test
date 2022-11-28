import os, secrets
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.guesser.guesser import Guesser
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.contracts.error.error import Error
from obscuro.test.networks.obscuro import Obscuro


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = Obscuro
        web3, account = network.connect_account1(self, web_socket=self.WEBSOCKET)

        guesser = Guesser(self, web3, 0, 100)
        guesser.deploy(network, account)

        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        error = Error(self, web3, 'foo')
        error.deploy(network, account)

    def storage_client(self, network, contract_address, abi_path, num):
        # run a background script to filter and collect events
        pk=secrets.token_hex(32)
        self.fund_obx(network, web3_user, account_user, self.OBX)

        stdout = os.path.join(self.output, 'storage_client_%d.out' % num)
        stderr = os.path.join(self.output, 'storage_client_%d.err' % num)
        script = os.path.join(self.input, 'storage_client.py')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--contract_address', '%s' % contract_address])
        args.extend(['--contract_abi', '%s' % abi_path])
        args.extend(['--pk_to_register', '%s' % Properties().account3pk()]
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting to run the event loop', timeout=10)