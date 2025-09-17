import os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.bridge import EthereumBridge


class PySysTest(TenNetworkTest):

    def execute(self):
        network = self.get_network_connection(name='local' if self.is_local_ten() else 'primary', verbose=False)
        web3, account = network.connect_account1(self)
        self.value = 100
        self.bridge = EthereumBridge(self, web3)
        self.bridge_fees = self.bridge.contract.functions.valueTransferFee().call()
        self.run_client(network, account.address)

    def run_client(self, network, receiver):
        pk = self.get_ephemeral_pk()
        web3, account = network.connect(self, private_key=pk, check_funds=False)
        self.distribute_native(account, network.ETH_ALLOC)

        stdout = os.path.join(self.output, 'client.out')
        stderr = os.path.join(self.output, 'client.err')
        script = os.path.join(self.input, 'client.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--chainId', '%s' % network.chain_id()])
        args.extend(['--bridge_address', '%s' % self.bridge.address])
        args.extend(['--bridge_abi', '%s' % self.bridge.abi_path])
        args.extend(['--bridge_fees', '%d' % self.bridge_fees])
        args.extend(['--pk', pk])
        args.extend(['--receiver', receiver])
        args.extend(['--amount', '%d' % self.value])
        self.run_python(script, stdout, stderr, args, workingDir=self.output)
        self.waitForSignal(file=stdout, expr='Starting client')
        self.waitForGrep(file=stdout, expr='Client completed', timeout=45)

