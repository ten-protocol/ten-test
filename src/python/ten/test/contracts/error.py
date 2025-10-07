from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class DeleteMapping(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'error', 'DeleteMapping.sol')
    CONTRACT = 'DeleteMapping'


class Error(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'error', 'Error.sol')
    CONTRACT = 'Error'


class ErrorTwoPhase(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'error', 'ErrorTwoPhase.sol')
    CONTRACT = 'ErrorTwoPhase'


class PayableConstructorRevert(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'error', 'PayableConstructorRevert.sol')
    CONTRACT = 'PayableConstructorRevert'


class SelfDestructOnDeploy(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'error', 'SelfDestructOnDeploy.sol')
    CONTRACT = 'SelfDestructOnDeploy'
