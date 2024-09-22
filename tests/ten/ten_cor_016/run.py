import re
from pysys.constants import FAILED
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.game import Game
from ten.test.helpers.log_subscriber import AllEventsLogSubscriber


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network and deploy the game
        network_dev = self.get_network_connection()
        web3_dev, account_dev = network_dev.connect_account2(self)
        game = Game(self, web3_dev)
        game.deploy(network_dev, account_dev)

        # run a background script to filter and collect events
        subscriber = AllEventsLogSubscriber(self, network_dev, game.address, game.abi_path)
        subscriber.run()

        # connect a user to the network
        network_usr = self.get_network_connection()
        web3_usr, account_usr = network_usr.connect_account1(self)
        game_usr = Game.clone(web3_usr, account_usr, game)

        try:
            target = int.from_bytes(web3_usr.eth.get_storage_at(game.address, 1))

            # this is the flow we'd expect if we were not on ten
            if not self.is_ten():
                self.log.info('Number to guess is %d', target)
                self.waitForGrep(file='subscriber.out', expr='Received event: Guessed')
                network_usr.transact(self, web3_usr, game_usr.contract.functions.guess(target), account_usr, game.GAS_LIMIT)
                self.assertOrderedGrep(file='subscriber.out', exprList=['success: true', 'secretNumber: \'%d\'' % target])
            else:
                self.addOutcome(FAILED, outcomeReason='Exception should be thrown')

        except ValueError as e:
            # this is the flow we expect on ten
            if self.is_ten():
                self.log.info('Exception type: %s', type(e).__name__)
                self.log.info('Exception args: %s', e.args)
                regex = re.compile('eth_getStorageAt is not supported for this contract', re.M)
                self.assertTrue(regex.search(e.args[0]['message']) is not None)
            else:
                self.addOutcome(FAILED, outcomeReason='Exception should not be thrown')
