import os
from pysys.constants import FAILED
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.bridge import EthereumBridge


class PySysTest(TenNetworkTest):

    def execute(self):
        # create network and connect
        network = self.get_network_connection()
        private_key = Properties().account1pk()
        web3, account = network.connect_account1(self)
        bridge = EthereumBridge(self, web3)

        # execute the transfer using ethers
        self.client(network, bridge.address, bridge.abi_path, private_key, account.address, 1000)

        self.addOutcome(FAILED)

    def client(self, network, address, abi_path, private_key, to, amount):
        # create the client
        stdout = os.path.join(self.output, 'client.out')
        stderr = os.path.join(self.output, 'client.err')
        script = os.path.join(self.input, 'client.js')
        args = []
        args.extend(['--network', network.connection_url()])
        args.extend(['--contract_address', address])
        args.extend(['--contract_abi', abi_path])
        args.extend(['--sender_pk', private_key])
        args.extend(['--to', to])
        args.extend(['--amount', str(amount)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting transactions', timeout=10)
        self.waitForGrep(file=stdout, expr='Completed transactions', timeout=40)
