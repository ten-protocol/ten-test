from pysys.constants import *
from obscuro.test.contracts import DefaultContract


class Game(DefaultContract):
    GAS_LIMIT = 4*720000
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessGame.sol')
    CONTRACT = 'GuessGame'

