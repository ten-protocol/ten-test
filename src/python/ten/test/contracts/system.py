import os.path, json
from pysys.constants import *
from ten.test.utils.properties import Properties
from ten.test.contracts.default import DefaultContract


class TenSystemCallsCaller(DefaultContract):
    SOURCE = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'system', 'TenSystemCallsCaller.sol')
    CONTRACT = 'TenSystemCallsCaller'


class TransactionPostProcessor:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_transaction_post_processor()
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'system', 'contracts',
                                     'TransactionPostProcessor.sol', 'TransactionPostProcessor.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class ZenTestnet:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3, address):
        self.test = test
        self.web3 = web3
        self.address = address
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'testing', 'ZenTestnet.sol',
                                     'ZenTestnet.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


