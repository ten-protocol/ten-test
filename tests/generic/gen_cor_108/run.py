import os
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import KeyStorage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = KeyStorage(self, web3)
        storage.deploy(network, account)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'block_notifier.out')
        stderr = os.path.join(self.output, 'block_notifier.err')
        script = os.path.join(self.input, 'block_notifier.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # wait a block time
        self.wait(float(self.block_time) * 2)

        # wait and validate
        self.waitForGrep(file='block_notifier.out', expr='Block =', condition='==1')
