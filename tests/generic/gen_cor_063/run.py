import os, json
from ethsys.basetest import EthereumTest
from ethsys.contracts.erc20.obx import OBXCoin
from ethsys.networks.factory import NetworkFactory
from ethsys.utils.properties import Properties
from ethsys.utils.keys import pk_to_account


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

        # run a background python script to pick up events
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        script = os.path.join(self.input, 'balance_poller.js')
        args = []
        args.extend(['-u', '%s' % network.connection_url(web_socket=False)])
        args.extend(['-a', '%s' % erc20.contract_address])
        args.extend(['-b', '%s' % abi_path])
        args.extend(['-p', '%s' % Properties().account2pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting to run the event loop', timeout=10)

        # transfer from account1 into account2
        #for i in range(0, 5):
        #    self.log.info('Account1 balance = %d ' % erc20.contract.functions.balanceOf(account1.address).call())
        #    network.transact(self, web3, erc20.contract.functions.transfer(account2.address, 1), account1, erc20.GAS)

        #self.waitForGrep(file=stdout, expr='New balance = 5', timeout=20)
        #self.assertGrep(file=stdout, expr='New balance = 5')
