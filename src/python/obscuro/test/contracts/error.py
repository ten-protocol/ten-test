from pysys.constants import *
from obscuro.test.contracts import BaseContract


class Error(BaseContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'error', 'Error.sol')
    CONTRACT = 'Error'
