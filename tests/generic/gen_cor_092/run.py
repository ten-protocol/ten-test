import os
from pysys.constants import FOREGROUND
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection(name='local')
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # perform some transactions with a sleep in between
        for i in range(0, 2): network.transact(self, web3, storage.contract.functions.store(i), account, storage.GAS_LIMIT)
        self.wait(float(self.block_time) * 1.1)

        # run viem and web3js clients
        self.get_events(network, storage, 'viem')
        self.get_events(network, storage, 'web3')

    def get_events(self, network, storage, lib):
        stdout = os.path.join(self.output, 'poller_%s.out'%lib)
        stderr = os.path.join(self.output, 'poller_%s.err'%lib)
        logout = os.path.join(self.output, 'poller_%s.log'%lib)
        script = os.path.join(self.input, 'poller_%s.js'%lib)
        args = []
        args.extend(['--network_http', network.connection_url(web_socket=False)])
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--chain_id', '%s' % network.chain_id()])
        args.extend(['--contract_address', '%s' % storage.address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args, state=FOREGROUND)
