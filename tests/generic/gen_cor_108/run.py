import os
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'block_notifier.out')
        stderr = os.path.join(self.output, 'block_notifier.err')
        script = os.path.join(self.input, 'block_notifier.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        # wait and validate
        self.waitForGrep(file='block_notifier.out', expr='Block =', condition='==4', timeout=120)

        # wait two block times and verify we only see 4
        self.wait(float(self.block_time) * 2)

        self.assertLineCount(file='block_notifier.out', expr='Block =', condition='==4')

