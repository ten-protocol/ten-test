from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGame
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network and deploy the game
        network_dev = self.get_network_connection()
        web3_dev, account_dev = network_dev.connect_account2(self)
        game = TransparentGuessGame(self, web3_dev)
        game.deploy(network_dev, account_dev)

        # run a background script to filter and collect events
        subscriber = AllEventsLogSubscriber(self, network_dev, game.address, game.abi_path)
        subscriber.run()

        # connect a user to the network
        network_usr = self.get_network_connection()
        web3_usr, account_usr = network_usr.connect_account1(self)
        game_usr = TransparentGuessGame.clone(web3_usr, account_usr, game)

        target = int.from_bytes(web3_usr.eth.get_storage_at(game.address, 1))
        self.log.info('Number to guess is %d', target)
        network_usr.transact(self, web3_usr, game_usr.contract.functions.guess(target), account_usr, game.GAS_LIMIT)
        self.waitForGrep(file='subscriber.out', expr='Full event', timeout=10)
        self.assertOrderedGrep(file='subscriber.out', exprList=['success: true', 'secretNumber: \'%d\'' % target])
