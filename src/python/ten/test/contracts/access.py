from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class ContractA(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'access', 'ContractA.sol')
    CONTRACT = 'ContractA'


class ContractB(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'access', 'ContractB.sol')
    CONTRACT = 'ContractB'