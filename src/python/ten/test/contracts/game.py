from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Game(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessGame.sol')
    CONTRACT = 'GuessGame'


class OpenStorageGuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'OpenStorageGuessGame.sol')
    CONTRACT = 'OpenStorageGuessGame'


class OpenEventGuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'OpenEventGuessGame.sol')
    CONTRACT = 'OpenEventGuessGame'

