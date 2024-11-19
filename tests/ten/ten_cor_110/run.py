from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.storage import StorageTwoPhaseNoEvents, StorageTwoPhaseWithEvents


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network via the primary gateway and deploy the contract
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        self.log.info('Running for StorageTwoPhaseNoEvents')
        self.run(StorageTwoPhaseNoEvents, network, web3, account, 203)

        self.log.info('Running for StorageTwoPhaseWithEvents')
        self.run(StorageTwoPhaseWithEvents, network, web3, account, 987)

    def run(self, contract, network, web3, account, num):
        # deploy the contract and check the initial value
        storage = contract(self, web3, 100, Properties().L2PublicCallbacks)
        storage.deploy(network, account)
        self.log.info('Call shows value %d', storage.contract.functions.retrieve().call())
        self.assertTrue(storage.contract.functions.retrieve().call() == 100)

        # log balance, then build the target with the value to give to the callback contract
        balance_before = web3.eth.get_balance(account.address)
        self.log.info('Balance before:   %d' % balance_before)
        target = storage.contract.functions.store(num)
        params = {'gasPrice': web3.eth.gas_price, 'value': web3.to_wei(0.01, 'ether')}
        gas_estimate = target.estimate_gas(params)
        params['gas'] = int(1.1*gas_estimate)
        build_tx = target.build_transaction(params)
        tx_receipt = network.tx(self, web3, build_tx, account)
        gas_used = int(tx_receipt['gasUsed'])

        # confirm the tx set the value and lo
        balance_after = web3.eth.get_balance(account.address)
        self.log.info('Call shows value: %d', storage.contract.functions.retrieve().call())
        self.log.info('Balance after:    %d' % balance_after)
        self.log.info('Balance change:   %d' % (balance_before-balance_after))
        self.log.info('Expected change:  %s' % (web3.to_wei(0.01, 'ether') + gas_used*web3.eth.gas_price))
        self.assertTrue(storage.contract.functions.retrieve().call() == num)
