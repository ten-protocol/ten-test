from obscuro.test.basetest import ObscuroNetworkTest
from obscuro.test.contracts.storage import Storage
from obscuro.test.helpers.wallet_extension import WalletExtension
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(ObscuroNetworkTest):

    def execute(self):
        wallet = WalletExtension.start(self, name='shared')
        network_connection_1 = self.get_network_connection(wallet=wallet)
        network_connection_2 = self.get_network_connection(wallet=wallet)

        web3_1, account_1 = network_connection_1.connect_account1(self)
        web3_2, account_2 = network_connection_1.connect_account2(self)
        web3_3, account_3 = network_connection_2.connect_account3(self)
        web3_4, account_4 = network_connection_2.connect_account4(self)

        storage = Storage(self, web3_1, 100)
        storage.deploy(network_connection_1, account_1)
        subscriber_1 = AllEventsLogSubscriber(self, network_connection_1, storage,
                                              stdout='subscriber_1.out',
                                              stderr='subscriber_2.err')
        subscriber_1.run()

        subscriber_2 = AllEventsLogSubscriber(self, network_connection_2, storage,
                                              stdout='subscriber_2.out',
                                              stderr='subscriber_2.err')
        subscriber_2.run()

        count = 0
        for (web3, account, network) in [(web3_1, account_1, network_connection_1),
                                         (web3_2, account_2, network_connection_1),
                                         (web3_3, account_3, network_connection_2),
                                         (web3_4, account_4, network_connection_2)]:
            count = count + 1
            network.transact(self, web3, storage.contract.functions.store(count), account, storage.GAS_LIMIT)
