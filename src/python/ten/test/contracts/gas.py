from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class GasConsumer(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'gas', 'GasConsumer.sol')
    CONTRACT = 'GuessGame'


class GasConsumerAdd(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'gas', 'GasConsumerAdd.sol')
    CONTRACT = 'GasConsumerAdd'


class GasConsumerMultiply(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'gas', 'GasConsumerMultiply.sol')
    CONTRACT = 'GasConsumerMultiply'


class GasConsumerBalance(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'gas', 'GasConsumerBalance.sol')
    CONTRACT = 'GasConsumerBalance'


