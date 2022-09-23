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
        web3, account_distro = network.connect(self, Properties().distro_account_pk(self.env))

        erc20 = OBXCoin(self, web3)
        erc20.deploy(network, account_distro)

        # dump out the abi
        abi_path = os.path.join(self.output, 'erc20.abi')
        with open(abi_path, 'w') as f: json.dump(erc20.abi, f)

        # run a background python script to pick up events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'event_listener.py')
        args = [network.connection_url(web_socket=False), erc20.contract_address, abi_path]
        if self.is_obscuro(): args.extend(['--pk', Properties().account2pk()])
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting to run the event loop', timeout=10)

        # transfer from account1 into account2
        for i in range(0, 5):
            self.log.info('Distro balance = %d ' % erc20.contract.functions.balanceOf(account_distro.address).call())
            network.transact(self, web3, erc20.contract.functions.transfer(account2.address, 1), account_distro, erc20.GAS)

        self.waitForGrep(file=stdout, expr='Balance = 5', timeout=20)


