import json
from solcx import compile_source
from pysys.constants import *
from obscuro.test.utils.properties import Properties


class Game:
    """Abstraction over the pay to play guessing game smart contract."""
    GAS_LIMIT = 4 * 720000

    def __init__(self, test, web3, range, token_address):
        """Create an instance of the ERC20 contract, compile and construct a web3 instance. """
        self.test = test
        self.web3 = web3
        self.range = range
        self.token = token_address
        self.bytecode = None
        self.abi = None
        self.abi_path = None
        self.contract = None
        self.address = None
        self.account = None
        self.construct()

    def construct(self):
        """Compile and construct an instance. """
        file = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'game', 'GuessGame.sol')
        with open(file, 'r') as fp:
            compiled_sol = compile_source(source=fp.read(), output_values=['abi', 'bin'],
                                          solc_binary=Properties().solc_binary(),
                                          base_path=os.path.dirname(file))
            contract_interface = compiled_sol['<stdin>:GuessGame']
            self.bytecode = contract_interface['bin']
            self.abi = contract_interface['abi']

        self.abi_path = os.path.join(self.test.output, 'guesser_token.abi')
        with open(self.abi_path, 'w') as f: json.dump(self.abi, f)

        self.contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode).constructor(self.range, self.token)

    def deploy(self, network, account):
        """Deploy the contract using a given account."""
        self.account = account
        tx_receipt = network.transact(self.test, self.web3, self.contract, account, self.GAS_LIMIT)
        self.address = tx_receipt.contractAddress
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)
        return tx_receipt