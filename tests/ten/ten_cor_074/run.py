import os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import FieldSenderRelevancy


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect the players to the network
        network_1 = self.get_network_connection()
        network_2 = self.get_network_connection()
        network_3 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account2(self)
        web3_3, account_3 = network_3.connect_account3(self)

        # player 3 deploys and interacts with the contract
        relevancy = FieldSenderRelevancy(self, web3_3)
        relevancy.deploy(network_3, account_3)
        target = relevancy.contract.functions.twoIndexedAddresses
        network_3.transact(self, web3_3, target(account_1.address, account_2.address), account_3, relevancy.GAS_LIMIT)
        block_number = web3_3.eth.get_block_number()

        # dev account can not see the TwoIndexedAddresses event
        logout_1 = self.get_logs(network_1, relevancy, block_number, '1')
        logout_2 = self.get_logs(network_2, relevancy, block_number, '2')
        logout_3 = self.get_logs(network_3, relevancy, block_number, '3')
        self.assertLineCount(file=logout_1, expr='TwoIndexedAddresses event:', condition='==1')
        self.assertLineCount(file=logout_2, expr='TwoIndexedAddresses event:', condition='==1')
        self.assertLineCount(file=logout_3, expr='TwoIndexedAddresses event:', condition='==1')

    def get_logs(self, network, contract, block_numer, name):
        # run a javascript by the dev to get past events
        self.log.info('Gett past events for %s'%name)
        stdout = os.path.join(self.output, 'poller_%s.out'%name)
        stderr = os.path.join(self.output, 'poller_%s.err'%name)
        logout = os.path.join(self.output, 'poller_%s.log'%name)
        script = os.path.join(self.input, 'poller.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % contract.address])
        args.extend(['--contract_abi', '%s' % contract.abi_path])
        args.extend(['--log_file', '%s' % logout])
        args.extend(['--from_block', '%s' % block_numer])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Completed task', timeout=30)
        return logout
