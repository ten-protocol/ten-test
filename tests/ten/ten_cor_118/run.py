import os
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.relevancy import Relevancy, RelevancyTwoPhase


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the storage and storage contract with two phase commit
        relevancy_two_phase = RelevancyTwoPhase(self, web3, Properties().L2PublicCallbacks)
        relevancy_two_phase.deploy(network, account)
        relevancy_normal = Relevancy(self, web3)
        relevancy_normal.deploy(network, account)

        # subscribe for CallerIndexedAddress events
        self.subscribe(relevancy_two_phase, network, 'relevancy_two_phase')
        self.subscribe(relevancy_normal, network, 'relevancy_normal')
        self.wait(float(self.block_time) * 1.1)

        # perform some transactions on both contracts
        for i in range(0, 5): self.transact(relevancy_two_phase, web3, network, account)
        network.transact(self, web3, relevancy_normal.contract.functions.callerIndexedAddress(),
                         account, relevancy_normal.GAS_LIMIT)
        self.waitForGrep('relevancy_two_phase.log', expr='Decoded address', condition='>=5')
        self.waitForGrep('relevancy_normal.log', expr='Decoded address', condition='>=1')
        self.assertLineCount('relevancy_two_phase.log', 'Decoded address = %s' % account.address, condition='==5')
        self.assertLineCount('relevancy_normal.log', 'Decoded address = %s' % account.address, condition='==1')

    def transact(self, relevancy, web3, network, account):
        target = relevancy.contract.functions.callerIndexedAddress()
        params = {'gasPrice': web3.eth.gas_price, 'value': web3.to_wei(0.01, 'ether')}
        gas_estimate = target.estimate_gas(params)
        params['gas'] = int(1.1 * gas_estimate)
        build_tx = target.build_transaction(params)
        network.tx(self, web3, build_tx, account)

    def subscribe(self, relevancy, network, name):
        # run a background script to filter and collect events
        stdout = os.path.join(self.output, '%s.out' % name)
        stderr = os.path.join(self.output, '%s.err' % name)
        logout = os.path.join(self.output, '%s.log' % name)
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % relevancy.address])
        args.extend(['--contract_abi', '%s' % relevancy.abi_path])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Started task ...', timeout=10)