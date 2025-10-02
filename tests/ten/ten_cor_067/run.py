import json, os
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import FieldNoOneGuessGame
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network_1 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        network_2 = self.get_network_connection()
        web3_2, account_2 = network_2.connect_account2(self)

        # player 1 deploys the contract and subscribes for events
        game_1 = FieldNoOneGuessGame(self, web3_1)
        game_1.deploy(network_1, account_1)
        subscriber1 = AllEventsLogSubscriber(self, network_1, game_1.address, game_1.abi_path,
                                             stdout='subscriber1.out', stderr='subscriber1.err')
        subscriber1.run()

        # player 2 transacts to guess the number
        game_2 = FieldNoOneGuessGame.clone(web3_2, account_2, game_1)
        subscriber2 = AllEventsLogSubscriber(self, network_2, game_2.address, game_2.abi_path,
                                             stdout='subscriber2.out', stderr='subscriber2.err')
        subscriber2.run()
        start_block_num = web3_2.eth.get_block_number()
        network_2.transact(self, web3_2, game_2.contract.functions.guess(1), account_2, game_2.GAS_LIMIT)

        # player 2 should see the Guessed and Attempts events as the config will be auto-visibility
        self.waitForGrep('subscriber2.out', expr='attempts:.*1', timeout=10)
        self.assertLineCount('subscriber2.out', expr='Received event: Guessed', condition='==1')
        self.assertLineCount('subscriber2.out', expr='Received event: Attempts', condition='==1')
        self.assertGrep('subscriber1.out', expr='Received event: Guessed', contains=False)
        self.assertGrep('subscriber1.out', expr='Received event: Attempts', contains=False)

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
            self.assertTrue(response[i]['eventConfigPublic'] == False)    # Field.EVERYONE is not set
            self.assertTrue(response[i]['eventAutoVisibility'] == True)   # we've defaulted to auto
            self.assertTrue(response[i]['topic1AutoRelevant'] == True)    # topic1 is indexed
            self.assertTrue(response[i]['topic2AutoRelevant'] == False)   # topic2 is not indexed
            self.assertTrue(response[i]['topic3AutoRelevant'] == False)   # topic3 is not indexed

    def dump(self, obj, filename):
        with open(os.path.join(self.output, filename), 'w') as file:
            json.dump(obj, file, indent=4)