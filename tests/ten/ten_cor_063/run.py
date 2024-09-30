from ten.test.basetest import TenNetworkTest
from ten.test.contracts.relevancy import RelevancyOneCantView
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network, deploy the contract, add a subscriber to the contract
        network_1 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        relevancy_1 = RelevancyOneCantView(self, web3_1)
        relevancy_1.deploy(network_1, account_1)
        AllEventsLogSubscriber(self, network_1, relevancy_1.address, relevancy_1.abi_path,
                              stdout='sub1.out', stderr='sub1.err').run()

        # connect a user to the network
        network_2 = self.get_network_connection()
        web3_2, account_2 = network_2.connect_account2(self)
        relevancy_2 = RelevancyOneCantView.clone(web3_2, account_2, relevancy_1)
        AllEventsLogSubscriber(self, network_2, relevancy_2.address, relevancy_2.abi_path,
                               stdout='sub2.out', stderr='sub2.err').run()

        network_2.transact(self, web3_2,
                           relevancy_2.contract.functions.twoIndexedAddresses(account_2.address, account_1.address),
                           account_2, relevancy_2.GAS_LIMIT)

        #self.waitForGrep('subscriber.out', expr='guessedNumber.*4')
        #self.assertLineCount('subscriber.out', expr='Received event: Guessed', condition='==4')
        #self.assertGrep('subscriber.out', expr='Received event: Attempts', contains=False)
