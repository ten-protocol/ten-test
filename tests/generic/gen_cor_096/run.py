import os
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.helpers.ws_proxy import WebServerProxy


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = KeyStorage(self, web3)
        storage.deploy(network, account)

        # go through a proxy to log websocket communications if needed
        ws_url = network.connection_url(web_socket=True)
        if self.PROXY: ws_url = WebServerProxy.create(self).run(ws_url, 'proxy.logs')

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'hash_notifier.out')
        stderr = os.path.join(self.output, 'hash_notifier.err')
        script = os.path.join(self.input, 'hash_notifier.js')
        args = []
        args.extend(['--network_ws', ws_url])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions with a sleep in between
        receipt1 = network.transact(self, web3, storage.contract.functions.setItem('key1', 1), account, storage.GAS_LIMIT)
        receipt2 = network.transact(self, web3, storage.contract.functions.setItem('key1', 2), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file='hash_notifier.out', expr='Mined', condition='==2')
        exprList = []
        exprList.append('Pending %s' % receipt1.transactionHash.hex())
        exprList.append('Mined %s' % receipt1.transactionHash.hex())
        exprList.append('Pending %s' % receipt2.transactionHash.hex())
        exprList.append('Mined %s' % receipt2.transactionHash.hex())
        self.assertOrderedGrep(file='hash_notifier.out', exprList=exprList)
