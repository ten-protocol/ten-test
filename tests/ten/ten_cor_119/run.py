from ten.test.basetest import TenNetworkTest
from ten.test.utils.properties import Properties
from ten.test.contracts.storage import StorageTwoPhaseWithRefund
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber

class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # deploy the contract
        storage = StorageTwoPhaseWithRefund(self, web3, 100, Properties().L2PublicCallbacks)
        storage.deploy(network, account)

        # run a background script to filter and collect events
        subscriber = AllEventsLogSubscriber(self, network, storage.address, storage.abi_path)
        subscriber.run()

        # transact against the contract
        balance_before = web3.eth.get_balance(account.address)
        estimate, used, price = self.transact(storage, web3, network, account, 200)
        self.wait(float(self.block_time) * 1.1)
        value = storage.contract.functions.retrieve().call()
        self.log.info('Retrieved value: %d' % value)
        self.assertTrue(storage.contract.functions.retrieve().call() == 200, assertMessage='Value should be 200')

        balance_after = web3.eth.get_balance(account.address)
        self.log.info('Balance before:  %d' % balance_before)
        self.log.info('Balance after:   %d' % balance_before)
        self.log.info('Balance diff:    %d' % (balance_before-balance_after))
        self.log.info('Expected diff:   %d' % ((used*price) + web3.to_wei(0.001, 'ether')))
        self.log.info('Cost estimate:   %d' % (estimate*price))
        self.log.info('Cost used:       %d' % (used*price))

        refund_balance = storage.contract.functions.refundBalance().call()
        self.log.info('Refund balance:  %d' % refund_balance)
        self.assertTrue(refund_balance != 0, assertMessage='Refund should not be zero')

        network.transact(self, web3, storage.contract.functions.refundWithdraw(), account, storage.GAS_LIMIT)
        balance_after_refund = web3.eth.get_balance(account.address)
        self.log.info('Balance refund:  %d' % balance_after_refund)

    def transact(self, storage, web3, network, account, num):
        target = storage.contract.functions.store(num)
        params = {'gasPrice': web3.eth.gas_price, 'value': web3.to_wei(0.001, 'ether'), 'chainId': web3.eth.chain_id}
        gas_estimate = target.estimate_gas(params)
        params['gas'] = gas_estimate
        build_tx = target.build_transaction(params)
        tx_receipt = network.tx(self, web3, build_tx, account, txstr='StorageTwoPhaseWithRefund.store(%d)'%num)
        return gas_estimate, int(tx_receipt['gasUsed']), int(tx_receipt['effectiveGasPrice'])

