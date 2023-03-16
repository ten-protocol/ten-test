from pysys.constants import *
from obscuro.test.contracts.default import DefaultContract


class ReceiveEther(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'payable', 'Payable.sol')
    CONTRACT = 'ReceiveEther'


class SendEther(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'payable', 'Payable.sol')
    CONTRACT = 'SendEther'
