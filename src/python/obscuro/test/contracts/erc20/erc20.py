import json
from pysys.constants import *


class ERC20Token:
    """Abstraction over a pre-deployed ERC20 smart contract. """
    GAS_LIMIT = 7200000

    def __init__(self, test, web3, name, symbol, address):
        """Construct an instance of the web3 contract class for a generic ERC20 contract. """
        self.test = test
        self.web3 = web3
        self.name = name
        self.symbol = symbol
        self.address = address
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)
