import os
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.bridge import EthereumBridge
from ten.test.contracts.bridge import L2MessageBus


class PySysTest(TenNetworkTest):

    def execute(self):
        # create network and connect
        network = self.get_network_connection()
        private_key = Properties().account1pk()
        web3, account = network.connect_account1(self)
        bridge = EthereumBridge(self, web3)
        bus = L2MessageBus(self, web3)

        # execute the transfer using ethers
        self.client(network, bridge.address, bridge.abi_path, bus.address, bus.abi_path, private_key, account.address, 1000)
        expr_list = []
        expr_list.append('Sender:   %s' % bridge.address)
        expr_list.append('Receiver: %s' % account.address)
        expr_list.append('Amount:   1000')
        self.assertOrderedGrep(file='client.out', exprList=expr_list)

    def client(self, network, bridge_address, bridge_abi, bus_address, bus_abi, private_key, to, amount):
        # create the client
        stdout = os.path.join(self.output, 'client.out')
        stderr = os.path.join(self.output, 'client.err')
        script = os.path.join(self.input, 'client.js')
        args = []
        args.extend(['--network', network.connection_url()])
        args.extend(['--bridge_address', bridge_address])
        args.extend(['--bridge_abi', bridge_abi])
        args.extend(['--bus_address', bus_address])
        args.extend(['--bus_abi', bus_abi])
        args.extend(['--sender_pk', private_key])
        args.extend(['--to', to])
        args.extend(['--amount', str(amount)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting transactions', timeout=10)
        self.waitForGrep(file=stdout, expr='Completed transactions', timeout=40)
