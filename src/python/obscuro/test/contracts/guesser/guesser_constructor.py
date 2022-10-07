import json, random
from solcx import compile_source
from pysys.constants import *
from obscuro.test.utils.properties import Properties
from obscuro.test.contracts.guesser.guesser import Guesser


class GuesserConstructor(Guesser):
    """Abstraction over the guessing game smart contract using a constructor."""

    def __init__(self, test, web3, lower=0, upper=100):
        """Call the parent constructor but set the secret first."""
        self.secret = random.randint(lower, upper)
        test.log.info('Secret number to guess will be %d' % self.secret)
        super().__init__(test, web3, lower=0, upper=100)

    def construct(self):
        """Compile and construct an instance."""
        file = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'guesser', 'Guesser_constructor.sol')
        with open(file, 'r') as fp:
            compiled_sol = compile_source(source=fp.read(), output_values=['abi', 'bin'],
                                          solc_binary=Properties().solc_binary())
            contract_id, contract_interface = compiled_sol.popitem()
            self.bytecode = contract_interface['bin']
            self.abi = contract_interface['abi']

        self.abi_path = os.path.join(self.test.output, 'guesser_constructor.abi')
        with open(self.abi_path, 'w') as f: json.dump(self.abi, f)

        self.contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode).constructor(self.secret)

