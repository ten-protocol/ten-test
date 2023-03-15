from pysys.constants import *
from obscuro.test.contracts import DefaultContract


class Relevancy(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'relevancy', 'Relevancy.sol')
    CONTRACT = 'Relevancy'

