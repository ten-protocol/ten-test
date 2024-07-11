import os
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.relevancy import Relevancy


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account1 = network.connect_account1(self)

        # deploy the storage contracts
        contract = Relevancy(self, web3)
        contract.deploy(network, account1)

        # run test specific event subscriber
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        logout = os.path.join(self.output, 'subscriber.log')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', account1.address])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Subscribed for event logs', timeout=10)

        # perform some transactions on the key storage contract
        network.transact(self, web3, contract.contract.functions.callerIndexedAddress(), account1, contract.GAS_LIMIT)
        self.wait(float(self.block_time) * 2.0)

        # wait and validate
        self.waitForGrep(file=logout, expr='Result =', timeout=20)
        self.assertLineCount(file=logout, expr='Result = ', condition='==1')
