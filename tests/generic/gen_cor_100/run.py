from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import Storage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # get contract address, or deploy
        storage = Storage(self, web3, 0)
        storage.get_or_deploy(network, account, persist_nonce=True)

        # retrieve the current value
        expected = storage.get_persisted_param('value', 0)
        actual = storage.contract.functions.retrieve().call()
        self.log.info('Last persisted value is stored as %d', expected)
        self.log.info('Current retrieved value is %d', actual)
        self.assertTrue(expected == actual)

        # set the value via a transaction and retrieve the new value
        self.log.info('Incrementing the current value by 1')
        tx_receipt = network.transact(self, web3, storage.contract.functions.store(actual+1), account, Storage.GAS_LIMIT)
        if tx_receipt.status == 1: storage.set_persisted_param('value', actual+1)
        else: self.log.warn('Transaction receipt showed error')

        actual_after = storage.contract.functions.retrieve().call()
        self.log.info('Current retrieved value is %d', actual_after)
        self.assertTrue(actual_after == actual+1)
