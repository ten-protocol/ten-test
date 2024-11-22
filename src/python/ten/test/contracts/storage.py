from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Storage(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'Storage.sol')
    CONTRACT = 'Storage'


class StorageTwoPhaseNoEvents(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'StorageTwoPhaseNoEvents.sol')
    CONTRACT = 'StorageTwoPhaseNoEvents'


class StorageTwoPhaseWithEvents(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'StorageTwoPhaseWithEvents.sol')
    CONTRACT = 'StorageTwoPhaseWithEvents'


class StorageTwoPhaseWithReceive(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'StorageTwoPhaseWithReceive.sol')
    CONTRACT = 'StorageTwoPhaseWithReceive'


class KeyStorage(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'KeyStorage.sol')
    CONTRACT = 'KeyStorage'

