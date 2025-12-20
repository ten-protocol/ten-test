import os.path, json
from pysys.constants import *
from ten.test.utils.properties import Properties


class WETH:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().weth_contract_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'weth', 'weth.sol')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

