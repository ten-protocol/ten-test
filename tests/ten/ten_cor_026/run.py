import os, re
from ten.test.utils.properties import Properties
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.bridge import EthereumBridge, L2MessageBus, L1CrossChainMessenger


class PySysTest(TenNetworkTest):

    def execute(self):
        transfer = 4000000000000000
        pk = self.get_ephemeral_pk()
        timeout = 90000 if self.is_local_ten() else 2400000 # 1min on a local, 40min otherwise

        # the l1 and l2 networks and connections
        l1 = self.get_l1_network_connection()
        l2 = self.get_network_connection()
        web3_l1, account_l1 = l1.connect(self, private_key=pk)
        web3_l2, account_l2 = l2.connect(self, private_key=pk)
        l1_before = web3_l1.eth.get_balance(account_l1.address)
        l2_before = web3_l2.eth.get_balance(account_l2.address)
        self.log.info('  l1_balance before:     %s', l1_before)
        self.log.info('  l2_balance before:     %s', l2_before)

        # the relevant contracts on the l1 and l2 networks
        xchain = L1CrossChainMessenger(self, web3_l1)
        bridge = EthereumBridge(self, web3_l2)
        bus = L2MessageBus(self, web3_l2)
        fees = bridge.contract.functions.valueTransferFee().call()

        # execute the transfer using ethers
        self.client(l2, bridge.address, bridge.abi_path, bus.address, bus.abi_path, pk,
                    l1, xchain.address, xchain.abi_path, account_l1.address, transfer+fees, timeout)
        l1_after = web3_l1.eth.get_balance(account_l1.address)
        l2_after = web3_l2.eth.get_balance(account_l2.address)
        l1_cost = self.get_cost()
        self.log.info('  l1_balance after:      %s', l1_after)
        self.log.info('  l2_balance after:      %s', l2_after)
        self.log.info('  l1_cost:               %s', l1_cost)
        self.log.info('  l1_delta (with cost):  %s', l1_after-l1_before+l1_cost)

        # validate the outcome
        self.assertTrue(l1_after-l1_before+l1_cost == transfer,
                        assertMessage='L1 balance should increase by transfer amount plus gas for releasing')


    def client(self, l2_network, bridge_address, bridge_abi, bus_address, bus_abi, private_key,
               l1_network, xchain_address, xchain_abi, to, amount, timeout):
        node_url = 'http://%s:%s' % (Properties().validator_host(self.env, self.NODE_HOST),
                                     Properties().validator_port_http(self.env))

        stdout = os.path.join(self.output, 'client.out')
        stderr = os.path.join(self.output, 'client.err')
        script = os.path.join(self.input, 'client.js')
        args = []
        args.extend(['--l2_network', l2_network.connection_url()])
        args.extend(['--l2_bridge_address', bridge_address])
        args.extend(['--l2_bridge_abi', bridge_abi])
        args.extend(['--l2_bus_address', bus_address])
        args.extend(['--l2_bus_abi', bus_abi])
        args.extend(['--l1_network', l1_network.connection_url()])
        args.extend(['--l1_xchain_address', xchain_address])
        args.extend(['--l1_xchain_abi', xchain_abi])
        args.extend(['--node_url', node_url])
        args.extend(['--pk', private_key])
        args.extend(['--to', to])
        args.extend(['--amount', str(amount)])
        args.extend(['--timeout', str(timeout)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting transaction to send funds to the L1', timeout=10)
        self.waitForGrep(file=stdout, expr='Completed transactions', timeout=timeout/1000)


    def get_cost(self):
        cost = None
        regex = re.compile('L1 cost:       (?P<cost>.*)$', re.M)
        with open(os.path.join(self.output, 'client.out'), 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: cost = result.group('cost')
        return int(cost)