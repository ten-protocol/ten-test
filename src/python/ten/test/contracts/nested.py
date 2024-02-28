from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class StoreAndRetrieve(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'nested', 'StoreAndRetrieve.sol')
    CONTRACT = 'StoreAndRetrieve'

