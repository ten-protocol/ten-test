import os.path, json
from pysys.constants import *
from ten.test.utils.properties import Properties


class CrossChainManagement:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_cross_chain_management_address()
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'l1_management', 'contracts', 'CrossChain.sol',
                                     'CrossChain.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L1MessageBus:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_message_bus_address()
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'cross_chain_messaging', 'common',
                                     'MessageBus.sol', 'MessageBus.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L2MessageBus:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_message_bus_address()
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'cross_chain_messaging', 'common',
                                     'MessageBus.sol', 'MessageBus.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L1CrossChainMessenger:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_cross_chain_messenger_address()
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'cross_chain_messaging', 'common',
                                     'CrossChainMessenger.sol', 'CrossChainMessenger.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L2CrossChainMessenger:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_cross_chain_messenger_address()
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'cross_chain_messaging', 'common',
                                     'CrossChainMessenger.sol', 'CrossChainMessenger.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class TenBridge:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_bridge_address()
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'reference_bridge', 'L1', 'contracts',
                                     'TenBridge.sol', 'TenBridge.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class EthereumBridge:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_bridge_address()
        self.abi_path =os.path.join(PROJECT.root, 'artifacts', 'contracts', 'reference_bridge', 'L2', 'contracts',
                                    'EthereumBridge.sol', 'EthereumBridge.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class TenERC20:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_bridge_address()
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'testing', 'TenERC20.sol', 'TenERC20.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class WrappedERC20:
    GAS_LIMIT = 3_000_000

    def __init__(self, test, web3, name, symbol, address):
        self.test = test
        self.web3 = web3
        self.name = name
        self.symbol = symbol
        self.address = address
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'testing', 'WrappedERC20.sol', 'WrappedERC20.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)