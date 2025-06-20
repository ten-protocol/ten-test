from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.storage import KeyStorage


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = self.get_network_connection()
        web3, account = network.connect_account1(self)

        # get contract address, or deploy
        storage = KeyStorage(self, web3)
        storage.get_or_deploy(network, account, persist_nonce=True)

        # retrieve the current value
        expected = int(storage.get_persisted_param('key', 0))
        actual = storage.contract.functions.getItem('key').call()
        self.log.info('Last persisted value is stored as %d', expected)
        self.log.info('Current retrieved value is %d', actual)
        self.assertTrue(expected == actual)

        # set the value via a transaction and retrieve the new value
        tx_receipt = network.transact(self, web3, storage.contract.functions.setItem('key', actual+1), account, KeyStorage.GAS_LIMIT)
        if tx_receipt.status == 1: storage.set_persisted_param('key', actual+1)
        self.wait(float(self.block_time) * 2.0)

        value_after = storage.contract.functions.getItem('key').call()
        self.log.info('Call shows value %d', value_after)
        self.assertTrue(value_after == actual + 1)
