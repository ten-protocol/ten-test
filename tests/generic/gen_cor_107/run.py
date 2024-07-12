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
        stdout = os.path.join(self.output, 'hash_notifier.out')
        stderr = os.path.join(self.output, 'hash_notifier.err')
        logout = os.path.join(self.output, 'hash_notifier.log')
        script = os.path.join(self.input, 'hash_notifier.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Starting task ...', timeout=10)

        # perform some transactions with a sleep in between
        receipt1 = network.transact(self, web3, storage.contract.functions.setItem('key1', 1), account, storage.GAS_LIMIT)
        receipt2 = network.transact(self, web3, storage.contract.functions.setItem('key1', 2), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=logout, expr='Mined', condition='==2', timeout=10)
        exprList = []
        exprList.append('Pending %s' % receipt1.transactionHash.hex())
        exprList.append('Mined %s' % receipt1.transactionHash.hex())
        exprList.append('Pending %s' % receipt2.transactionHash.hex())
        exprList.append('Mined %s' % receipt2.transactionHash.hex())
        self.assertOrderedGrep(file=logout, exprList=exprList)
