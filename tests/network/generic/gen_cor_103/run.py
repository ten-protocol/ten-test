import os
from web3 import Web3
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):
    ITERATIONS = 10
    CLIENTS = 5

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        balance_before = web3.eth.get_balance(account.address)
        self.client(network, account.address, 100)
        balance_after = web3.eth.get_balance(account.address)
        self.log.info('Balance before: %d', balance_before)
        self.log.info('Balance after: %d', balance_after)
        self.assertTrue(balance_after == (balance_before + 100))

    def client(self, network, to, amount):
        private_key = self.get_ephemeral_pk()
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC_EPHEMERAL)
        network.connect(self, private_key=private_key, check_funds=False)

        # create the client
        stdout = os.path.join(self.output, 'client.out')
        stderr = os.path.join(self.output, 'client.err')
        logout = os.path.join(self.output, 'client.log')
        script = os.path.join(self.input, 'client.js')
        args = []
        args.extend(['--network', network.connection_url()])
        args.extend(['--private_key', private_key])
        args.extend(['--to', to])
        args.extend(['--amount', str(amount)])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting transactions', timeout=10)
        self.waitForGrep(file=logout, expr='Completed transactions', timeout=40)
