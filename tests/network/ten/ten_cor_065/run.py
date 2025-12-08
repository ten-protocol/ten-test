import os, json
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
        tx_receipt = network_3.transact(self, web3_3, target(account_1.address, account_2.address), account_3, relevancy.GAS_LIMIT)

        # all accounts should be able to see the event (account 3 as they are the sender, account 1 and 2 as the
        # references their addresses as indexed fields
        self.waitForGrep(file=subscriber_1.stdout, expr='Received event: TwoIndexedAddresses')
        self.waitForGrep(file=subscriber_2.stdout, expr='Received event: TwoIndexedAddresses')
        self.waitForGrep(file=subscriber_3.stdout, expr='Received event: TwoIndexedAddresses')
        self.assertLineCount(file=subscriber_1.stdout, expr='Received event: TwoIndexedAddresses', condition='==1')
        self.assertLineCount(file=subscriber_2.stdout, expr='Received event: TwoIndexedAddresses', condition='==1')
        self.assertLineCount(file=subscriber_3.stdout, expr='Received event: TwoIndexedAddresses', condition='==1')

        # assert get_debug_event_log_relevancy for the TwoIndexedAddresses events
        response = self.get_debug_event_log_relevancy(url=network_3.connection_url(),
                                                      address=relevancy.address,
                                                      signature=web3_3.keccak(text='TwoIndexedAddresses(address,address)').hex(),
                                                      fromBlock=hex(tx_receipt.blockNumber), toBlock='latest')

        self.dump(response, 'response_event.log')
        self.log.info('Assert get_debug_event_log_relevancy for event')
        self.assertTrue(len(response) == 1)
        self.assertTrue(response[0]['defaultContract'] == False)      # there is a config
        self.assertTrue(response[0]['transparentContract'] == False)  # ContractCfg.PRIVATE is set
        self.assertTrue(response[0]['eventConfigPublic'] == False)    # Field.EVERYONE is not set
        self.assertTrue(response[0]['topic1Relevant'] == True)        # Field.TOPIC1 is set
        self.assertTrue(response[0]['topic2Relevant'] == True)        # Field.TOPIC2 is set
        self.assertTrue(response[0]['topic3Relevant'] == False)       # Field.TOPIC3 is not set
        self.assertTrue(response[0]['senderRelevant'] == True)        # Field.SENDER is set

    def dump(self, obj, filename):
        with open(os.path.join(self.output, filename), 'w') as file:
            json.dump(obj, file, indent=4)

    def subscribe(self, network, contract, name):
        # run a javascript by the dev to get past events
        self.log.info('Subscribing for all events for %s' % name)
        subscriber = AllEventsLogSubscriber(self, network, contract.address, contract.abi_path,
                                            stdout='%s.out' % name, stderr='%s.err' % name)
        subscriber.run()
        return subscriber

