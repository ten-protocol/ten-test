import json
from pysys.constants import *
from obscuro.test.contracts.default import DefaultContract


class ERC20Token:
    GAS_LIMIT = 10*720000

    def __init__(self, test, web3, name, symbol, address):
        self.test = test
        self.web3 = web3
        self.name = name
        self.symbol = symbol
        self.address = address
        self.abi_path = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')
        with open(self.abi_path) as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class MintedERC20Token(DefaultContract):
    GAS_LIMIT = 4*720000

    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'MintedERC20.sol')
    CONTRACT = 'MintedERC20'
