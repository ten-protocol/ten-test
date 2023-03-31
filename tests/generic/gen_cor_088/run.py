import os
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.relevancy import Relevancy
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.helpers.ws_proxy import WebServerProxy


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        contract = Relevancy(self, web3)
        contract.deploy(network, account)

        # go through a proxy to log websocket communications if needed
        ws_url = network.connection_url(web_socket=True)
        ws_url = WebServerProxy.create(self).run(ws_url, 'proxy.logs')

        # run test specific event subscriber
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', ws_url])
        args.extend(['--address', account.address])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Subscribed for event logs', timeout=10)

        # perform some transactions on the key storage contract
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account, contract.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=stdout, expr='Result =', timeout=20)

