from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Game(DefaultContract):
    GAS_LIMIT = 4 * 720000
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessGame.sol')
    CONTRACT = 'GuessGame'


class Token(DefaultContract):
    GAS_LIMIT = 4 * 720000
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessToken.sol')
    CONTRACT = 'GuessToken'
