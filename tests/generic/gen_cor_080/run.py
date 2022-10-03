import os, json, time
from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.storage import Storage
from ethsys.networks.factory import NetworkFactory
from ethsys.utils.properties import Properties


class PySysTest(EthereumTest):
    PROXY = False

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the contract, dump out the abi, make some transactions
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        tx_recp1 = network.transact(self, web3, storage.contract.functions.store(0), account, storage.GAS)
        tx_recp2 = network.transact(self, web3, storage.contract.functions.store(1), account, storage.GAS)
        tx_recp3 = network.transact(self, web3, storage.contract.functions.store(2), account, storage.GAS)
        from_block = tx_recp2.blockNumber

        # go through a proxy to log websocket comms if needed
        ws_url = network.connection_url(web_socket=True)
        if self.PROXY:
            ws_url = self.run_ws_proxy(ws_url, 'proxy.logs')
            self.log.info('Using websocket proxy on url %s' % ws_url)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'listener.out')
        stderr = os.path.join(self.output, 'listener.err')
        script = os.path.join(self.input, 'event_listener.js')
        args = []
        args.extend(['--url_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--url_ws', '%s' % ws_url])
        args.extend(['--from_block', '%d' % from_block])
        args.extend(['--pk', '%s' % Properties().account3pk()])
        if self.is_obscuro(): args.append('--obscuro')
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some more transactions
        for i in range(3, 6):
            network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS)
            time.sleep(1.0)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Stored value', condition='== 5', timeout=20)
        self.assertOrderedGrep(file=stdout, exprList=['Stored value = %d' % x for x in range(1, 6)])
