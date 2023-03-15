from pysys.constants import *
from obscuro.test.contracts import DefaultContract


class KeyStorage(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'KeyStorage.sol')
    CONTRACT = 'KeyStorage'

