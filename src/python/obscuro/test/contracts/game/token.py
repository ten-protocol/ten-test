from pysys.constants import *
from obscuro.test.contracts import DefaultContract


class Token(DefaultContract):
    GAS_LIMIT = 4*720000
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessToken.sol')
    CONTRACT = 'GuessToken'
