from web3 import Web3
from obscuro.test.basetest import GenericNetworkTest
from obscuro.test.contracts.game.token import Token
from obscuro.test.contracts.game.game import Game
from obscuro.test.networks.factory import NetworkFactory
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.log_subscriber import AllEventsLogSubscriber

class PySysTest(GenericNetworkTest):

    def execute(self):
        # deployment of contract
        network = NetworkFactory.get_network(self)
        web3, account = network.connect_account1(self)

        token = Token(self, web3)
        token.deploy(network, account)

        game = Game(self, web3, 10, token.address)
        game.deploy(network, account)

        # run a background script to filter and collect events
        subscriber = AllEventsLogSubscriber(self, network, game,
                                            stdout='subscriber.out',
                                            stderr='subscriber.err')
        subscriber.run(Properties().account3pk(), network.connection_url(), network.connection_url(True))

        # approve the game to spend tokens on behalf of the user
        web3_player, account_player = network.connect_account2(self)

        token_player = web3_player.eth.contract(address=token.address, abi=token.abi)
        network.transact(self, web3_player, token_player.functions.approve(game.address, Web3().toWei(10, 'ether')), account_player, game.GAS_LIMIT)

        # play the game
        game_player = web3_player.eth.contract(address=game.address, abi=game.abi)
        for i in range(0,9):
            allowance = token_player.functions.allowance(account_player.address, game.address).call({"from":account_player.address})
            balance = token_player.functions.balanceOf(account_player.address).call({"from":account_player.address})
            self.log.info('Allowance is %.3f' % Web3().fromWei(allowance, 'ether'))
            self.log.info('Balance is %.3f' % Web3().fromWei(balance, 'ether'))
            network.transact(self, web3, game_player.functions.attempt(i), account_player, game.GAS_LIMIT)

