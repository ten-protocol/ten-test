from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class IncrementerV1(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'proxy', 'IncrementerV1.sol')
    CONTRACT = 'ReceiveEther'


class IncrementerV2(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'proxy', 'IncrementerV2.sol')
    CONTRACT = 'SendEther'
