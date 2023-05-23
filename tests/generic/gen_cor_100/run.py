import json
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to network
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # get contract address, or deploy
        storage = Storage(self, web3, 0)
        storage.get_or_deploy(network, account, persist_nonce=True)

        # retrieve the current value
        value = storage.contract.functions.retrieve().call()
        self.log.info('Call shows value %d' % value)

        # set the value via a transaction and retrieve the new value
        network.transact(self, web3, storage.contract.functions.store(value+1), account, Storage.GAS_LIMIT)
        value_after = storage.contract.functions.retrieve().call()
        self.log.info('Call shows value %d' % value_after)
        self.assertTrue(value_after == value+1)
