from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import FieldEveryoneAllEventsGuessGame
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network_1 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account1(self)
        network_2 = self.get_network_connection()
        web3_2, account_2 = network_2.connect_account2(self)

        # player 1 deploys the contract and subscribes for events
        game_1 = FieldEveryoneAllEventsGuessGame(self, web3_1)
        game_1.deploy(network_1, account_1)
        subscriber1 = AllEventsLogSubscriber(self, network_1, game_1.address, game_1.abi_path,
                                             stdout='subscriber1.out', stderr='subscriber1.err')
        subscriber1.run()

        # player 2 transacts to guess the number
        game_2 = FieldEveryoneAllEventsGuessGame.clone(web3_2, account_2, game_1)
        subscriber2 = AllEventsLogSubscriber(self, network_2, game_2.address, game_2.abi_path,
                                             stdout='subscriber2.out', stderr='subscriber2.err')
        subscriber2.run()
        for i in range(1, 5):
            self.log.info('Number to guess is %d', i)
            network_2.transact(self, web3_2, game_2.contract.functions.guess(i), account_2, game_2.GAS_LIMIT)

        # player 2 should see just the Attempts event, player 1 should not see any
        self.waitForGrep('subscriber2.out', expr='attempts:.*4', timeout=10)
        self.assertLineCount('subscriber2.out', expr='Received event: Guessed', condition='==4')
        self.assertLineCount('subscriber2.out', expr='Received event: Attempts', condition='==4')
        self.assertLineCount('subscriber1.out', expr='Received event: Guessed', condition='==4')
        self.assertLineCount('subscriber1.out', expr='Received event: Attempts', condition='==4')

