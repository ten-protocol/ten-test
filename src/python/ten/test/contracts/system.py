from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class TenSystemCallsCaller(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'system', 'TenSystemCallsCaller.sol')
    CONTRACT = 'TenSystemCallsCaller'







