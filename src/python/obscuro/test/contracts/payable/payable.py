from pysys.constants import *
from obscuro.test.contracts import DefaultContract


class ReceiveEther(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'payable', 'Payable.sol')
    CONTRACT = 'ReceiveEther'
