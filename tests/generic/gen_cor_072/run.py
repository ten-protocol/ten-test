import os, time
from obscuro.test.basetest import EthereumTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the contract and dump out the abi
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'event_listener.py')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--contract_address', '%s' % storage.contract_address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        if self.is_obscuro(): args.extend(['--pk_to_register', '%s' % Properties().account3pk()])
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting to run the event loop', timeout=10)

        # perform some transactions
        for i in range(0,5):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS)
            time.sleep(1.0)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Stored value', condition='== 5', timeout=20)
        self.assertOrderedGrep(file=stdout, exprList=['Stored value = %d' % x for x in range(0, 5)])

