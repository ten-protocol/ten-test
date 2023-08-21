import os
from web3 import Web3
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.erc20 import MintedERC20Token
from obscuro.test.utils.properties import Properties


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = self.get_network_connection()
        web3, account1 = network.connect_account1(self)
        _, account2 = network.connect_account2(self)

        erc20 = MintedERC20Token(self, web3, 'OBXCoin', 'OBX', 1000000)
        erc20.deploy(network, account1)

        # run a background script to poll for balance
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        script = os.path.join(self.input, 'balance_poller.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--address', '%s' % erc20.address])
        args.extend(['--contract_abi', '%s' % erc20.abi_path])
        args.extend(['--polling_address', '%s' % account2.address])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting to run the polling loop', timeout=10)

        # transfer from account1 into account2
        for i in range(0, 5):
            self.log.info('Account1 balance = %d ', erc20.contract.functions.balanceOf(account1.address).call())
            network.transact(self, web3, erc20.contract.functions.transfer(account2.address, 1), account1, erc20.GAS_LIMIT)

        self.waitForGrep(file=stdout, expr='New balance = 5', timeout=20)
        self.assertGrep(file=stdout, expr='New balance = 5')
