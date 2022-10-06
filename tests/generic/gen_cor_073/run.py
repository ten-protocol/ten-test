import os, json, time
from obscuro.test.basetest import EthereumTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties


class PySysTest(EthereumTest):
    PROXY = False

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the contract and dump out the abi
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)
        abi_path = os.path.join(self.output, 'storage.abi')
        with open(abi_path, 'w') as f:
            json.dump(storage.abi, f)

        # go through a proxy to log websocket comms is needed
        ws_url = network.connection_url(web_socket=True)
        if self.PROXY:
            ws_url = self.run_ws_proxy(ws_url, 'proxy.logs')
            self.log.info('Using websocket proxy on url %s' % ws_url)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'poller.out')
        stderr = os.path.join(self.output, 'poller.err')
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % network.connection_url(web_socket=True)])
        args.extend(['--contract_address', '%s' % storage.contract_address])
        args.extend(['--contract_abi', '%s' % abi_path])
        if self.is_obscuro(): args.extend(['--pk_to_register', '%s' % Properties().account3pk()])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions
        for i in range(0, 5):
            tx_receipt = network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Stored value', condition='== 5', timeout=20)
        self.assertOrderedGrep(file=stdout, exprList=['Stored value = %d' % x for x in range(0, 5)])

