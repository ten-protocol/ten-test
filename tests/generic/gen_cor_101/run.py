from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import KeyStorage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # get contract address, or deploy
        storage = KeyStorage(self, web3)
        storage.get_or_deploy(network, account, persist_nonce=True)

        # retrieve the current value
        value = storage.contract.functions.getItem('key').call()
        self.log.info('Call shows value %d', value)

        # set the value via a transaction and retrieve the new value
        network.transact(self, web3, storage.contract.functions.setItem('key', value+1), account, KeyStorage.GAS_LIMIT)
        value_after = storage.contract.functions.getItem('key').call()
        self.log.info('Call shows value %d', value_after)
        self.assertTrue(value_after == value + 1)
