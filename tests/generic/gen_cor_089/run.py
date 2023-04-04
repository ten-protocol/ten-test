import os
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.relevancy import Relevancy
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.helpers.ws_proxy import WebServerProxy


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account1 = network.connect_account1(self)

        # deploy the storage contracts
        contract = Relevancy(self, web3)
        contract.deploy(network, account1)

        # go through a proxy to log websocket communications if needed
        ws_url = network.connection_url(web_socket=True)
        ws_url = WebServerProxy.create(self).run(ws_url, 'proxy.logs')

        # run test specific event subscriber
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', ws_url])
        args.extend(['--address', account1.address])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscribed for event logs', timeout=10)

        # perform some transactions on the key storage contract
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account1, contract.GAS_LIMIT)
        self.wait(float(self.block_time) * 2.0)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Result =', timeout=20)
        exprList = []
        exprList.append('Result =')
        exprList.append('topics')
        exprList.append('0xfee74d7ba76b50e00cddc7a9272495f4b15537b41c964eb4e2e6345a84ac8bcc')
        exprList.append('0x000000000000000000000000025c2f7473eebd20e6a8cb4ebb96465a5c09d5a3')
        self.assertOrderedGrep(file='subscriber.out', exprList=exprList)
        if not self.ALLOW_EVENT_DUPLICATES:
            self.assertLineCount(file=stdout, expr='Result = ', condition='==1')
