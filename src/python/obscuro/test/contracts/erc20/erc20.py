import json
from pysys.constants import *


class ERC20Token:
    """Abstraction over the ERC20 smart contract used locally."""
    GAS_LIMIT = 7200000

    def __init__(self, test, web3, name, symbol, address):
        """Create an instance of the ERC20 contract, compile and construct a web3 instance. """
        self.contract = None
        self.address = address
        self.test = test
        self.web3 = web3
        self.name = name
        self.symbol = symbol
        self.construct()

    def construct(self):
        """Compile and construct an instance."""
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            self.contract = self.web3.eth.contract(address=self.address, abi=json.load(f))
