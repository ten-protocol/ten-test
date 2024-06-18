import os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.emitter import EventEmitter


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to network on the primary gateway  and deploy contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        emitter = EventEmitter(self, web3, 100)
        emitter.deploy(network, account)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % emitter.address])
        args.extend(['--contract_abi', '%s' % emitter.abi_path])
        args.extend(['--id_filter', '1'])
        args.extend(['--sender_filter', account.address])
        args.extend(['--user_address_filter', account.address])
        args.extend(['--key_filter', '1'])
        args.extend(['--value_filter', '1'])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Listening for filtered events...', timeout=10)
