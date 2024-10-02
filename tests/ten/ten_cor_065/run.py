from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import FieldSenderRelevancy
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect the accounts to the network
        network_1 = self.get_network_connection()
        network_2 = self.get_network_connection()
        network_3 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        web3_2, account_2 = network_2.connect_account2(self)
        web3_3, account_3 = network_3.connect_account3(self)

        # account 3 deploys the contract, all accounts subscribe, then account3 transacts
        relevancy = FieldSenderRelevancy(self, web3_3)
        relevancy.deploy(network_3, account_3)
        subscriber_1 = self.subscribe(network_1, relevancy, '1')
        subscriber_2 = self.subscribe(network_2, relevancy, '2')
        subscriber_3 = self.subscribe(network_3, relevancy, '3')
        target = relevancy.contract.functions.twoIndexedAddresses
        network_3.transact(self, web3_3, target(account_1.address, account_2.address), account_3, relevancy.GAS_LIMIT)

        # all accounts should be able to see the event (account 3 as they are the sender, account 1 and 2 as the
        # references their addresses as indexed fields
        self.assertLineCount(file=subscriber_1.stdout, expr='Received event: TwoIndexedAddresses', condition='==1')
        self.assertLineCount(file=subscriber_2.stdout, expr='Received event: TwoIndexedAddresses', condition='==1')
        self.assertLineCount(file=subscriber_3.stdout, expr='Received event: TwoIndexedAddresses', condition='==1')

    def subscribe(self, network, contract, name):
        # run a javascript by the dev to get past events
        self.log.info('Subscribing for all events for %s' % name)
        subscriber = AllEventsLogSubscriber(self, network, contract.address, contract.abi_path,
                                            stdout='%s.out' % name, stderr='%s.err' % name)
        subscriber.run()
        return subscriber

