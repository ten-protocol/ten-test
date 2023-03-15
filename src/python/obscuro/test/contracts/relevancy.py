from pysys.constants import *
from obscuro.test.contracts import BaseContract


class Relevancy(BaseContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'relevancy', 'Relevancy.sol')
    CONTRACT = 'Relevancy'

