from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Game(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessGame.sol')
    CONTRACT = 'GuessGame'


class TransparentGuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'TransparentGuessGame.sol')
    CONTRACT = 'TransparentGuessGame'


class PublicEventGuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'PublicEventGuessGame.sol')
    CONTRACT = 'PublicEventGuessGame'


class Topic1CanViewGuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'Topic1CanViewGuessGame.sol')
    CONTRACT = 'Topic1CanViewGuessGame'


class Topic2CanViewGuessGame(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'Topic1CanViewGuessGame.sol')
    CONTRACT = 'Topic1CanViewGuessGame'



