from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Game(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessGame.sol')
    CONTRACT = 'GuessGame'
    

class TransparentGuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'TransparentGuessGame.sol')
    CONTRACT = 'TransparentGuessGame'


class FieldEveryoneGuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'FieldEveryoneGuessGame.sol')
    CONTRACT = 'FieldEveryoneGuessGame'


class FieldTopic1GuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'FieldTopic1GuessGame.sol')
    CONTRACT = 'FieldTopic1GuessGame'


class FieldTopic2GuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'FieldTopic2GuessGame.sol')
    CONTRACT = 'FieldTopic2GuessGame'


class FieldEveryoneAllEventsGuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'FieldEveryoneAllEventsGuessGame.sol')
    CONTRACT = 'FieldEveryoneAllEventsGuessGame'


