from pysys.constants import *
from obscuro.test.contracts.default import DefaultContract


class Fibonacci(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'fibonacci', 'Fibonacci.sol')
    CONTRACT = 'FibonacciStorage'
