import json
from pysys.constants import *
from obscuro.test.contracts.default import DefaultContract


class ERC20Token:
    GAS_LIMIT = 7200000

    def __init__(self, test, web3, name, symbol, address):
        self.test = test
        self.web3 = web3
        self.name = name
        self.symbol = symbol
        self.address = address
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class MintedERC20Token(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'MintedERC20.sol')
    CONTRACT = 'MintedERC20'
