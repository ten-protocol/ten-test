import json
from pysys.constants import *
from ten.test.utils.properties import Properties


class TestUSDC:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.name = 'TestUSDC'
        self.symbol = 'USDC'
        self.address = Properties().market_usdc_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'market', 'contracts', 'test', 'TestUSDC.sol',
                                     'TestUSDC.json')
        with open(self.abi_path) as fp:
            self.abi = json.load(fp)["abi"]
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class TestTEN:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.name = 'TEN'
        self.symbol = 'TEN'
        self.address = Properties().market_ten_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'market', 'contracts', 'test', 'TestTEN.sol',
                                     'TestTEN.json')
        with open(self.abi_path) as fp:
            self.abi = json.load(fp)["abi"]
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class MarketPlace:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.name = 'TEN'
        self.symbol = 'TEN'
        self.address = Properties().market_place_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'market', 'contracts', 'marketplace', 'Marketplace.sol',
                                     'Marketplace.json')
        with open(self.abi_path) as fp:
            self.abi = json.load(fp)["abi"]
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class SellerNFT:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3, address):
        self.test = test
        self.web3 = web3
        self.address = address
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'market', 'contracts', 'marketplace', 'SellerReceipt.sol',
                                     'SellerReceipt.json')
        with open(self.abi_path) as fp:
            self.abi = json.load(fp)["abi"]
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)