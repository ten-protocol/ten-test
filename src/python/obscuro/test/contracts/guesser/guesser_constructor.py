import random
from pysys.constants import *
from obscuro.test.contracts.guesser.guesser import Guesser


class GuesserConstructor(Guesser):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'guesser', 'Guesser_constructor.sol')
    CONTRACT = 'GuesserConstructor'

    def __init__(self, test, web3, *args):
        """Call the parent constructor but set the secret first."""
        self.lower = args[0]
        self.upper =  args[1]
        self.secret = random.randint(args[0], args[1])
        test.log.info('Secret number to guess will be %d' % self.secret)
        super().__init__(test, web3, self.secret)

    def guess(self, max_guesses=100):
        """Perform a guessing game to get the secret number."""
        lower = self.lower
        upper = self.upper
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
                self.test.log.info("Guess is %d, need to go higher" % guess)
                lower = guess+1
            elif ret == -1:
                self.test.log.info("Guess is %d, need to go lower" % guess)
                upper = guess
            else:
                self.test.log.info("You've guessed the secret %s" % guess)
                self.test.addOutcome(PASSED)
                return guess