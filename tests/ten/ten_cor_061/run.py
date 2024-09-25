from ten.test.basetest import TenNetworkTest
from ten.test.contracts.game import TransparentGuessGameOneFile
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(TenNetworkTest):

    def execute(self):
        # connect to the network and deploy the game
        network_dev = self.get_network_connection()
        web3_dev, account_dev = network_dev.connect_account2(self)
        game = TransparentGuessGameOneFile(self, web3_dev)
        game.deploy(network_dev, account_dev)

        # connect a user to the network
        network_usr = self.get_network_connection()
        web3_usr, account_usr = network_usr.connect_account1(self)
        game_usr = TransparentGuessGameOneFile.clone(web3_usr, account_usr, game)

        # run a background script to filter and collect events
        subscriber = AllEventsLogSubscriber(self, network_dev, game.address, game.abi_path)
        subscriber.run()

        tx_recp = None
        for i in range(1,5):
            self.log.info('Number to guess is %d', i)
            tx_recp = network_usr.transact(self, web3_usr, game_usr.contract.functions.guess(i), account_usr, game.GAS_LIMIT)

        response = self.get_debug_event_log_relevancy(tx_recp.transactionHash.hex())
        self.log.info(response)

        self.waitForGrep('subscriber.out', expr='Received event', condition='==8', timeout=10)
        self.assertLineCount('subscriber.out', expr='Received event: Guessed', condition='==4')
        self.assertLineCount('subscriber.out', expr='Received event: Attempts', condition='==4')