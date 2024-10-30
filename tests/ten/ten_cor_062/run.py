import os, json
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import FieldEveryoneGuessGame
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network_1 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        network_2 = self.get_network_connection()
        web3_2, account_2 = network_2.connect_account2(self)

        # player 1 deploys the contract and subscribes for events
        game_1 = FieldEveryoneGuessGame(self, web3_1)
        game_1.deploy(network_1, account_1)
        subscriber = AllEventsLogSubscriber(self, network_1, game_1.address, game_1.abi_path)
        subscriber.run()

        # player 2 transacts to guess the number
        game_2 = FieldEveryoneGuessGame.clone(web3_2, account_2, game_1)
        start_block_num = web3_2.eth.get_block_number()
        for i in range(1, 5):
            self.log.info('Number to guess is %d', i)
            network_2.transact(self, web3_2, game_2.contract.functions.guess(i), account_2, game_2.GAS_LIMIT)

        # the contract is private, but Guess is for everyone, therefore player 2 should see the guessed
        # events but not the attempts events
        self.waitForGrep('subscriber.out', expr='guessedNumber.*4', timeout=10)
        self.assertLineCount('subscriber.out', expr='Received event: Guessed', condition='==4')
        self.assertGrep('subscriber.out', expr='Received event: Attempts', contains=False)

        # assert get_debug_event_log_relevancy for the guessed events
        response = self.get_debug_event_log_relevancy(url=network_1.connection_url(),
                                                      address=game_1.address,
                                                      signature=web3_1.keccak(text='Guessed(address,uint256,bool,uint256)').hex(),
                                                      fromBlock=hex(start_block_num), toBlock='latest')

        for i in range(0, len(response)):
            self.dump(response[i], 'response_event_%d.log' % i)
            self.log.info('Assert get_debug_event_log_relevancy for event %d' % i)
            self.assertTrue(response[i]['defaultContract'] == False)      # there is a config
            self.assertTrue(response[i]['transparentContract'] == False)  # ContractCfg.PRIVATE is set
            self.assertTrue(response[i]['eventConfigPublic'] == True)     # Field.EVERYONE is set
            self.assertTrue(response[i]['topic1Relevant'] == None)        # Field.TOPIC1 is not set
            self.assertTrue(response[i]['topic2Relevant'] == None)        # Field.TOPIC2 is not set
            self.assertTrue(response[i]['topic3Relevant'] == None)        # Field.TOPIC3 is not set
            self.assertTrue(response[i]['senderRelevant'] == None)        # Field.SENDER is not set
            self.log.info(response[i]['senderRelevant'])

    def dump(self, obj, filename):
        with open(os.path.join(self.output, filename), 'w') as file:
            json.dump(obj, file, indent=4)