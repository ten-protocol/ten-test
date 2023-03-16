from pysys.constants import *
from obscuro.test.contracts.default import DefaultContract


class Storage(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'Storage.sol')
    CONTRACT = 'Storage'


class KeyStorage(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'KeyStorage.sol')
    CONTRACT = 'KeyStorage'

