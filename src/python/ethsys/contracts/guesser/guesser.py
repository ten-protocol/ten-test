import random
from solcx import compile_source
from pysys.constants import *
from ethsys.utils.process import Processes


class Guesser:
    """Abstraction over the guessing game smart contract using a constructor."""
    GAS = 4*720000

    def __init__(self, test, web3, lower=0, upper=100):
        """Create an instance of the guesser contract, compile and construct a web3 instance."""
        self.bytecode = None
        self.abi = None
        self.contract = None
        self.contract_address = None
        self.account = None
        self.test = test
        self.web3 = web3
        self.lower = lower
        self.upper = upper
        self.construct()

    def construct(self):
        """Compile and construct an instance. """
        file = os.path.join(PROJECT.root, 'src', 'solidity', 'guesser', 'Guesser.sol')
        with open(file, 'r') as fp:
            compiled_sol = compile_source(source=fp.read(), output_values=['abi', 'bin'],
                                          solc_binary=Processes.get_solidity_compiler())
            contract_id, contract_interface = compiled_sol.popitem()
            self.bytecode = contract_interface['bin']
            self.abi = contract_interface['abi']

        self.contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode).constructor()

    def deploy(self, network, account):
        """Deploy the contract using a given account."""
        self.account = account
        tx_receipt = network.transact(self.test, self.web3, self.contract, account, self.GAS)
        self.contract_address = tx_receipt.contractAddress
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.abi)
        return tx_receipt

    def guess(self, max_guesses=100):
        """Perform a guessing game to get the secret number."""
        lower = self.lower
        upper = self.upper + 1
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
