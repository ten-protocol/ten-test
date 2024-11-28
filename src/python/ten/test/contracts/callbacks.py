from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class LargeCallData(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'callbacks', 'LargeCallData.sol')
    CONTRACT = 'LargeCallData'



