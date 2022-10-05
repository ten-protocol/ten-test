import os, requests
from ethsys.basetest import EthereumTest
from ethsys.contracts.storage.storage import Storage
from ethsys.networks.factory import NetworkFactory
from ethsys.utils.properties import Properties


class PySysTest(EthereumTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self.env)
        web3, account = network.connect_account1(self)

        # deploy the storage contracts
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # run a background script
        port = self.getNextAvailableTCPPort()
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--script_server_port', '%d' % port])
        args.extend(['--network_http', '%s' % network.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % network.connection_url(web_socket=True)])
        args.extend(['--contract_address', '%s' % storage.contract_address])
        args.extend(['--account_private_key', '%s' % Properties().account3pk()])
        if self.is_obscuro(): args.append('--is_obscuro')

        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Listening at http', timeout=10)

        requests.post('http://127.0.0.1:%d' % port, data='SUBSCRIBE', headers={'Content-Type': 'text/plain'})
        requests.post('http://127.0.0.1:%d' % port, data='UNSUBSCRIBE', headers={'Content-Type': 'text/plain'})
