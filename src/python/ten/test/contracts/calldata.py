from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class CallData(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'calldata', 'CallData.sol')
    CONTRACT = 'CallData'


class CallDataTwoPhase(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'calldata', 'CallDataTwoPhase.sol')
    CONTRACT = 'CallDataTwoPhase'



