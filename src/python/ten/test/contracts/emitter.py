from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class EventEmitter(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'emitter', 'EventEmitter.sol')
    CONTRACT = 'EventEmitter'


class TransparentEventEmitter(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'emitter', 'TransparentEventEmitter.sol')
    CONTRACT = 'TransparentEventEmitter'


class EventEmitterCaller(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'emitter', 'EventEmitterCaller.sol')
    CONTRACT = 'EventEmitterCaller'



