from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Create2Factory(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'create2', 'Create2Factory.sol')
    CONTRACT = 'Create2Factory'


class WrappedNative(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'create2', 'WrappedNative.sol')
    CONTRACT = 'WrappedNative'




