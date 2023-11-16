import random
from pysys.constants import *
from ten.test.contracts.default import DefaultContract


class Guesser(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'guesser', 'Guesser.sol')
    CONTRACT = 'Guesser'

    def guess(self, ilower, iupper, max_guesses=100):
        """Perform a guessing game to get the secret number."""
        lower = ilower
        upper = iupper
        nguess = 0
        while True:
            nguess += 1
            if nguess > max_guesses:
                self.test .log.warn("Exceeded guess count ... exiting")
                self.test .addOutcome(FAILED)
                return None

            guess = random.randrange(lower, upper)
            ret = self.contract.functions.guess(guess).call()
            if ret == 1:
                self.test.log.info("Guess is %d, need to go higher", guess)
                lower = guess+1
            elif ret == -1:
                self.test.log.info("Guess is %d, need to go lower", guess)
                upper = guess
            else:
                self.test.log.info("You've guessed the secret %s", guess)
                self.test.addOutcome(PASSED)
                return guess


class GuesserConstructor(Guesser):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'guesser', 'Guesser_constructor.sol')
    CONTRACT = 'GuesserConstructor'

