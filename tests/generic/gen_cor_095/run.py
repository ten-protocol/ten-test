import os
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import KeyStorage
from obscuro.test.helpers.ws_proxy import WebServerProxy


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = KeyStorage(self, web3)
        storage.deploy(network, account)

        # go through a proxy to log websocket communications if needed
        ws_url = network.connection_url(web_socket=True)
        if self.PROXY: ws_url = WebServerProxy.create(self).run(ws_url, 'proxy.logs')

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'block_notifier.out')
        stderr = os.path.join(self.output, 'block_notifier.err')
        script = os.path.join(self.input, 'block_notifier.js')
        args = []
        args.extend(['--network_ws', ws_url])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # perform some transactions with a sleep in between
        receipt1 = network.transact(self, web3, storage.contract.functions.setItem('key1', 1), account, storage.GAS_LIMIT)
        receipt2 = network.transact(self, web3, storage.contract.functions.setItem('key1', 2), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file='block_notifier.out', expr='Block =', condition='==2')
        exprList = []
        exprList.append('Block = [0-9]+ , Transaction = %s' % receipt1.transactionHash.hex())
        exprList.append('Block = [0-9]+ , Transaction = %s' % receipt2.transactionHash.hex())
        self.assertOrderedGrep(file='block_notifier.out', exprList=exprList)
