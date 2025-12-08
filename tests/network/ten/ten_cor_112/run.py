import os
from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.storage import StorageTwoPhaseWithEvents


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = StorageTwoPhaseWithEvents(self, web3, 100, Properties().L2PublicCallbacks)
        storage.deploy(network, account)

        # run a background script to filter and collect events
        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        logout = os.path.join(self.output, 'subscriber.log')
        script = os.path.join(self.input, 'subscriber.js')
        args = []
        args.extend(['--network_ws', network.connection_url(web_socket=True)])
        args.extend(['--address', '%s' % storage.address])
        args.extend(['--contract_abi', '%s' % storage.abi_path])
        args.extend(['--log_file', '%s' % logout])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=logout, expr='Started task ...', timeout=10)
        self.wait(float(self.block_time) * 1.1)

        for i in range(0, 5): self.transact(storage, web3, network, account, i)
        self.wait(float(self.block_time) * 1.1)

        # wait and validate
        self.waitForGrep(file=logout, expr='Stored value = 4', timeout=20)
        self.assertOrderedGrep(file=logout, exprList=['Stored value = %d' % x for x in range(0, 5)])
        self.assertLineCount(file=logout, expr='Stored value', condition='== 5')

    def transact(self, storage, web3, network, account, num):
        target = storage.contract.functions.store(num)
        params = {'gasPrice': web3.eth.gas_price, 'value': web3.to_wei(0.01, 'ether'), 'chainId': web3.eth.chain_id}
        params['gas'] = target.estimate_gas(params)
        build_tx = target.build_transaction(params)
        network.tx(self, web3, build_tx, account)
