import os, json
from obscuro.test.basetest import EthereumTest
from obscuro.test.contracts.erc20.obx import OBXCoin
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties
from obscuro.test.utils.keys import pk_to_account


class PySysTest(EthereumTest):
    WEBSOCKET = False

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self.env)
        account2 = pk_to_account(Properties().account2pk())
        web3, account1 = network.connect_account1(self, web_socket=self.WEBSOCKET)

        erc20 = OBXCoin(self, web3)
        erc20.deploy(network, account1)

        # dump out the abi
        abi_path = os.path.join(self.output, 'erc20.abi')
        with open(abi_path, 'w') as f: json.dump(erc20.abi, f)

        # run a background script to poll for balance
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        script = os.path.join(self.input, 'balance_poller.py')
        args = []
        args.extend(['-u', '%s' % network.connection_url(web_socket=False)])
        args.extend(['-a', '%s' % erc20.contract_address])
        args.extend(['-b', '%s' % abi_path])
        args.extend(['-p', '%s' % Properties().account2pk()])
        if self.is_obscuro(): args.append('--obscuro')
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting to run the polling loop', timeout=10)

        # transfer from account1 into account2
        for i in range(0, 5):
            self.log.info('Account1 balance = %d ' % erc20.contract.functions.balanceOf(account1.address).call())
            network.transact(self, web3, erc20.contract.functions.transfer(account2.address, 1), account1, erc20.GAS)

        self.waitForGrep(file=stdout, expr='New balance = 5', timeout=20)
        self.assertGrep(file=stdout, expr='New balance = 5')

