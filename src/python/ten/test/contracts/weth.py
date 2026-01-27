import os.path, json
from pysys.constants import *


class WETH:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3, address):
        self.test = test
        self.web3 = web3
        self.name = 'WETH'
        self.symbol = 'WETH'
        self.address = address
        self.abi_path = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'weth', 'weth.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

#web3.to_checksum_address(Properties().l1_weth_contract_address(test.env))