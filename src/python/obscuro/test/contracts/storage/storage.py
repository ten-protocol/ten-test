from pysys.constants import *
from obscuro.test.contracts import DefaultContract


class Storage(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'Storage.sol')
    CONTRACT = 'Storage'

