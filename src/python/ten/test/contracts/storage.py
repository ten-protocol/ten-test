from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Storage(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'Storage.sol')
    CONTRACT = 'Storage'


class StorageForUpgrades(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'StorageForUpgrades.sol')
    CONTRACT = 'StorageForUpgrades'


class StorageTwoPhaseNoEvents(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'StorageTwoPhaseNoEvents.sol')
    CONTRACT = 'StorageTwoPhaseNoEvents'


class StorageTwoPhaseWithEvents(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'StorageTwoPhaseWithEvents.sol')
    CONTRACT = 'StorageTwoPhaseWithEvents'


class StorageTwoPhaseReceiveWithRevert(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'StorageTwoPhaseReceiveWithRevert.sol')
    CONTRACT = 'StorageTwoPhaseReceiveWithRevert'


class StorageTwoPhaseWithRefund(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'StorageTwoPhaseWithRefund.sol')
    CONTRACT = 'StorageTwoPhaseWithRefund'


class KeyStorage(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'KeyStorage.sol')
    CONTRACT = 'KeyStorage'


class KeyStorageForUpgrades(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'storage', 'KeyStorageForUpgrades.sol')
    CONTRACT = 'KeyStorageForUpgrades'




