import json, os
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):

    def execute(self):
        # get the game address and the jam token address from the properties
        network = Obscuro
        game_address = Properties().guessing_game_address(self.env)
        hoc_address = Properties().l2_hoc_token_address(self.env)

        # get the connections for the game user
        #web3, account = network.connect(Properties().gameuserpk(), network.HOST, network.PORT)
        web3, account = network.connect_account1()
        self.log.info('Game contract address is %s' % game_address)
        self.log.info('Game user account is %s' % account.address)

        # the user needs to get the token and game contracts to interact with them
        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3.eth.contract(address=hoc_address, abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'guesser', 'guessing_game.abi')) as f:
            game = web3.eth.contract(address=game_address, abi=json.load(f))

        self.log.info('Game user JAM balance %d' % token.functions.balanceOf(account.address).call())
        #self.log.info('Prize funds is %d ' % game.functions.getBalance().call())
        self.log.info(web3.eth.get_balance(account.address))

        for i in range(0,5):
            self.log.info('Guessing number as %d' % i)
            network.transact(self, web3, token.functions.approve(game_address, 1), account, 720000 * 4)
            network.transact(self, web3, game.functions.attempt(i), account, 720000 * 4)

            #prize = game.functions.getBalance().call()
            #if prize == 0:
            #    self.log.info('Game balance is zero so user guess the right number')
            #    self.log.info('User balance is %d' % token.functions.balanceOf(account.address).call())
            #    break
            #else:
            #    self.log.info('Prize funds is %d ' % game.functions.getBalance().call())
            #    self.log.info('User balance is %d' % token.functions.balanceOf(account.address).call())