from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Game(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessGame.sol')
    CONTRACT = 'GuessGame'


class OpenGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'OpenGuessGame.sol')
    CONTRACT = 'OpenGuessGame'