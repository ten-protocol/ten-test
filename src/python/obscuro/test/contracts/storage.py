from pysys.constants import *
from obscuro.test.contracts import BaseContract


class Storage(BaseContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'Storage.sol')
    CONTRACT = 'Storage'


class KeyStorage(BaseContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'KeyStorage.sol')
    CONTRACT = 'KeyStorage'

