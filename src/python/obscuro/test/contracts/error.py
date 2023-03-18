from pysys.constants import *
from obscuro.test.contracts.default import DefaultContract


class Error(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'error', 'Error.sol')
    CONTRACT = 'Error'
