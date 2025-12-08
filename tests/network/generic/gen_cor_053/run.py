import os
from web3 import Web3
from ten.test.contracts.error import Error
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network and deploy the contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        error = Error(self, web3)
        error.deploy(network, account)

        # the two clients use an ephemeral test account that will leak funds but means
        # we don't need to manage the nonce
        self.client(network, error, 'ethers')
        self.client(network, error, 'web3')
        self.assertGrep(file='client_ethers.log', expr='Error: transaction failed')
        self.assertGrep(file='client_web3.log', expr='Error: Transaction has been reverted by the EVM')

    def client(self, network, contract, type):
        private_key = self.get_ephemeral_pk()
        self.distribute_native(Web3().eth.account.from_key(private_key), network.ETH_ALLOC_EPHEMERAL)
        network.connect(self, private_key=private_key, check_funds=False)

        # create the client
        stdout = os.path.join(self.output, 'client_%s.out' % type)
        stderr = os.path.join(self.output, 'client_%s.err' % type)
        logout = os.path.join(self.output, 'client_%s.log' % type)
        script = os.path.join(self.input, 'client_%s.js' % type)
        args = []
        args.extend(['--network', network.connection_url()])
        args.extend(['--address', contract.address])
        args.extend(['--contract_abi', contract.abi_path])
        args.extend(['--private_key', private_key])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting transactions', timeout=10)
        self.waitForGrep(file=logout, expr='Completed transactions', timeout=40)

