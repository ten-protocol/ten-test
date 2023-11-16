from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class ExpensiveContract(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'expensive', 'ExpensiveContract.sol')
    CONTRACT = 'FibonacciStorage'
