import os
from ten.test.basetest import GenericNetworkTest
from ten.test.contracts.game import Game


class PySysTest(GenericNetworkTest):

    def execute(self):
        # connect to the network and deploy the game
        network_dev = self.get_network_connection()
        web3_dev, account_dev = network_dev.connect_account2(self, web_socket=True)

        game = Game(self, web3_dev)
        game.deploy(network_dev, account_dev)

        # connect a user to the network for them to play the game
        network_usr = self.get_network_connection()
        web3_usr, account_usr = network_usr.connect_account1(self, web_socket=True)

        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'listener.js')
        args = []
        args.extend(['--network_http', '%s' % network_usr.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % network_usr.connection_url(web_socket=True)])
        args.extend(['--game_address', '%s' % game.address])
        args.extend(['--game_abi', '%s' % game.abi_path])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Registered all subscriptions', timeout=10)

        # play the game (we clone so that the abstraction use the users web3 and account details)
        game_usr = Game.clone(web3_usr, account_usr, game)
        for i in range(1,11):
            self.log.info('Guessing with number=%d', i)
            network_usr.transact(self, web3_usr, game_usr.contract.functions.guess(i), account_usr, game.GAS_LIMIT)
            self.waitForSignal(file='subscriber.out', filedir=self.output, expr='Your guess of %d' % i, timeout=20)

        self.assertLineCount(file='subscriber.out', expr='Your guess of', condition='==10')

