from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.storage.storage import Storage
from obscuro.test.networks.factory import NetworkFactory


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        # get the transaction count
        count_1 = web3.eth.get_transaction_count(account.address)
        self.log.info('Count 1: %d' % count_1)

        # deploy the contract
        storage = Storage(self, web3, 100)
        storage.deploy(network, account)

        # get the transaction count
        count_2 = web3.eth.get_transaction_count(account.address)
        self.log.info('Count 2: %d' % count_2)

        # interact with the contract
        network.transact(self, web3, storage.contract.functions.store(200), account, storage.GAS_LIMIT)

        # get the transaction count
        count_3 = web3.eth.get_transaction_count(account.address)
        self.log.info('Count 3: %d' % count_3)

        self.assertTrue(count_2 - count_1 == 1)
        self.assertTrue(count_3 - count_2 == 1)
