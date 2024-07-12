import os
from web3 import Web3
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.relevancy import Relevancy
from ten.test.utils.properties import Properties


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account1 = network.connect_account1(self)

        account2 = Web3().eth.account.from_key(Properties().account2pk())

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
        network.transact(self, web3, contract.contract.functions.indexedAddressAndNumber(account2.address), account1, contract.GAS_LIMIT)
        network.transact(self, web3, contract.contract.functions.indexedAddressAndNumber(account1.address), account1, contract.GAS_LIMIT)
        self.wait(float(self.block_time) * 2.0)

        # wait and validate
        self.waitForGrep(file=logout, expr='Result =', timeout=20)
        self.assertGrep(file=logout, expr='Result = 1', contains=False)
        self.assertLineCount(file=logout, expr='Result = 2', condition='==1')
