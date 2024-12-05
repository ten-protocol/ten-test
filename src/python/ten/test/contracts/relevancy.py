from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Relevancy(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'relevancy', 'Relevancy.sol')
    CONTRACT = 'Relevancy'


class FieldSenderRelevancy(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'relevancy', 'FieldSenderRelevancy.sol')
    CONTRACT = 'FieldSenderRelevancy'


class RelevancyTwoPhase(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'relevancy', 'RelevancyTwoPhase.sol')
    CONTRACT = 'RelevancyTwoPhase'

