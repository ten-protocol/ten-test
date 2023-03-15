from pysys.constants import *
from obscuro.test.contracts import BaseContract


class Game(BaseContract):
    GAS_LIMIT = 4*720000
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessGame.sol')
    CONTRACT = 'GuessGame'


class Token(BaseContract):
    GAS_LIMIT = 4*720000
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessToken.sol')
    CONTRACT = 'GuessToken'
