import sys
from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect players to the network
        network_1 = self.get_network_connection()
        web3_1, account_1 = network_1.connect_account2(self)
        network_2 = self.get_network_connection()
        web3_2, account_2 = network_2.connect_account1(self)

        # player 1 deploys the contract
        game_1 = TransparentGuessGame(self, web3_1)
        game_1.deploy(network_1, account_1)

        # player 2 subscribes for events, gets the secret number, and plays
        game_2 = TransparentGuessGame.clone(web3_2, account_2, game_1)
        subscriber = AllEventsLogSubscriber(self, network_2, game_2.address, game_2.abi_path)
        subscriber.run()

        target = int.from_bytes(web3_2.eth.get_storage_at(game_2.address, 1), sys.byteorder)
        self.log.info('Number to guess is %d', target)
        network_2.transact(self, web3_2, game_2.contract.functions.guess(target), account_2, game_2.GAS_LIMIT)

        # player 2 should see the events from player 2s interactions
        self.waitForGrep(file='subscriber.out', expr='Full event', timeout=10)
        self.assertOrderedGrep(file='subscriber.out', exprList=['success: true', 'secretNumber: \'%d\'' % target])
