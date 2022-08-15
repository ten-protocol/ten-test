import json, os
from pysys.constants import PROJECT
from ethsys.basetest import EthereumTest
from ethsys.utils.properties import Properties
from ethsys.networks.obscuro import Obscuro


class PySysTest(EthereumTest):

    def execute(self):
        # get the game address and the jam token address from the properties
        network = Obscuro
        game_address = Properties().guessing_game_address(network.PROPS_KEY)
        jam_address = Properties().l2_jam_token_address(network.PROPS_KEY)

        # get the connections for the game user
        web3_user, game_user = network.connect(Properties().gameuserpk(), network.HOST, network.PORT)
        self.log.info('Game contract address is %s' % game_address)
        self.log.info('Game user account is %s' % game_user.address)

        # the user needs to get the token and game contracts to interact with them
        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'erc20', 'erc20.json')) as f:
            jam_contract = web3_user.eth.contract(address=jam_address, abi=json.load(f))

        with open(os.path.join(PROJECT.root, 'utils', 'contracts', 'guesser', 'guessing_game.abi')) as f:
            game_contract = web3_user.eth.contract(address=game_address, abi=json.load(f))

        self.log.info('Game user JAM balance %d' % jam_contract.functions.balanceOf(game_user.address).call())
        self.log.info('Game balance is %d ' % game_contract.functions.getBalance().call())

        # the user starts making guesses (first needs to approve the game to take tokens)
        self.log.info('Guessing number')
        network.transact(self, web3_user, jam_contract.functions.approve(game_address, 1), game_user, 720000 * 4)
        network.transact(self, web3_user, game_contract.functions.attempt(23), game_user, 720000 * 4)


