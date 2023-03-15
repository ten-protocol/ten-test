from pysys.constants import *
from obscuro.test.contracts import BaseContract


class ReceiveEther(BaseContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'payable', 'Payable.sol')
    CONTRACT = 'ReceiveEther'
