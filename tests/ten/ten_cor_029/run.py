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

        # create and start the clients
        signal_file = os.path.join(self.output, '.signal')
        stdout_one = self.run_client(network, account.address, signal_file, name='one')
        stdout_two = self.run_client(network, account.address, signal_file, name='two')
        with open(signal_file, 'w') as sig: sig.write('go')

        # wait for the client to complete
        self.waitForGrep(file=stdout_one, expr='Client completed', timeout=45)
        self.waitForGrep(file=stdout_two, expr='Client completed', timeout=45)

    def run_client(self, network, receiver, signal_file, name):
        sender_pk = self.get_ephemeral_pk()
        web3, account = network.connect(self, private_key=sender_pk, check_funds=False)
        self.distribute_native(account, network.ETH_ALLOC)

        stdout = os.path.join(self.output, 'client_%s.out' % name)
        stderr = os.path.join(self.output, 'client_%s.err' % name)
        script = os.path.join(self.input, 'client.py')
        args = []
        args.extend(['--network_http', network.connection_url()])
        args.extend(['--chainId', '%s' % network.chain_id()])
        args.extend(['--bridge_address', '%s' % self.bridge.address])
        args.extend(['--bridge_abi', '%s' % self.bridge.abi_path])
        args.extend(['--bridge_fees', '%d' % self.bridge_fees])
        args.extend(['--sender_pk', sender_pk])
        args.extend(['--receiver', receiver])
        args.extend(['--amount', '%d' % self.value])
        args.extend(['--signal_file', signal_file])
        self.run_python(script, stdout, stderr, args, workingDir=self.output)
        self.waitForSignal(file=stdout, expr='Starting client')
        return stdout


