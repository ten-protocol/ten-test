from pysys.constants import *
from obscuro.test.contracts import BaseContract


class Game(BaseContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'gas', 'GasConsumer.sol')
    CONTRACT = 'GuessGame'


class GasConsumerAdd(BaseContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'gas', 'GasConsumerAdd.sol')
    CONTRACT = 'GasConsumerAdd'


class GasConsumerMultiply(BaseContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'gas', 'GasConsumerMultiply.sol')
    CONTRACT = 'GasConsumerMultiply'


class GasConsumerBalance(BaseContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'gas', 'GasConsumerBalance.sol')
    CONTRACT = 'GasConsumerBalance'


