import os
from ten.test.basetest import GenericNetworkTest


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'block_notifier.out')
        stderr = os.path.join(self.output, 'block_notifier.err')
        script = os.path.join(self.input, 'block_notifier.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Starting task ...', timeout=10)

        block_number_initial = web3.eth.get_block_number()
        self.log.info('Initial block number after starting task is %d', block_number_initial)

        # wait and validate we only see one block
        self.waitForGrep(file='block_notifier.out', expr='Block =', abortOnError=False)
        self.assertLineCount(file='block_notifier.out', expr='Block =', condition='==1')

        block_number_final = web3.eth.get_block_number()
        self.log.info('Final block number after running test is %d', block_number_final)