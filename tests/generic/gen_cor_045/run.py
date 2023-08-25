import os
from web3 import Web3
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.game import Token, Game
from obscuro.test.utils.properties import Properties


class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network_dev = self.get_network_connection(name='dev_connection')
        web3_dev, account_dev = network_dev.connect_account2(self)
        token = Token(self, web3_dev)
        token.deploy(network_dev, account_dev)
        game = Game(self, web3_dev, 9, token.address)
        game.deploy(network_dev, account_dev)

        # end usr playing the game
        network_usr = self.get_network_connection(name='usr_connection')
        web3_usr, account_usr = network_usr.connect_account1(self)

        stdout = os.path.join(self.output, 'subscriber.out')
        stderr = os.path.join(self.output, 'subscriber.err')
        script = os.path.join(self.input, 'listener.js')
        args = []
        args.extend(['--network_http', '%s' % network_usr.connection_url(web_socket=False)])
        args.extend(['--network_ws', '%s' % network_usr.connection_url(web_socket=True)])
        args.extend(['--erc_address', '%s' % token.address])
        args.extend(['--erc_abi', '%s' % token.abi_path])
        args.extend(['--game_address', '%s' % game.address])
        args.extend(['--game_abi', '%s' % game.abi_path])
        self.run_javascript(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Registered all subscriptions', timeout=10)

        # approve the game to spend tokens on behalf of the user
        token_player = web3_usr.eth.contract(address=token.address, abi=token.abi)
        network_usr.transact(self, web3_usr, token_player.functions.approve(game.address, Web3().toWei(10, 'ether')), account_usr, game.GAS_LIMIT)

        # play the game
        game_player = web3_usr.eth.contract(address=game.address, abi=game.abi)
        expected = []
        for i in range(0,10):
            self.log.info('Guessing with number=%d', i)
            expected.append('Your guess of %d' % i)
            allowance = token_player.functions.allowance(account_usr.address, game.address).call({"gas":1000000, "from":account_usr.address})
            balance = token_player.functions.balanceOf(account_usr.address).call({"gas":1000000, "from":account_usr.address})
            self.log.info('Allowance is %.3f', Web3().fromWei(allowance, 'ether'))
            self.log.info('Balance is %.3f', Web3().fromWei(balance, 'ether'))
            network_usr.transact(self, web3_usr, game_player.functions.attempt(i), account_usr, game.GAS_LIMIT)
            self.waitForSignal(file='subscriber.out', filedir=self.output, expr='Your guess of %d' % i, timeout=20)

        # we should have won at some point, and all are guesses should have been logged
        self.waitForSignal(file='subscriber.out', filedir=self.output,
                           expr='Congratulations.*Your guess of.*has won you the prize of.*OGG', timeout=20)

        self.assertOrderedGrep(file='subscriber.out', exprList=expected)

