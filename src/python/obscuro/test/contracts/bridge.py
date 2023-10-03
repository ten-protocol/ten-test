import os.path, json
from pysys.constants import *
from obscuro.test.utils.properties import Properties


class Management:
    GAS_LIMIT = 4*7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_bridge_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'management', 'ManagementContract.sol',
                                     'ManagementContract.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L1MessageBus:
    GAS_LIMIT = 4*7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_message_bus_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'MessageBus.sol',
                                     'MessageBus.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L2MessageBus:
    GAS_LIMIT = 4*7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_message_bus_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'MessageBus.sol',
                                     'MessageBus.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L1CrossChainMessenger:
    GAS_LIMIT = 4*7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_cross_chain_messenger_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'messenger',
                                     'CrossChainMessenger.sol', 'CrossChainMessenger.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L2CrossChainMessenger:
    GAS_LIMIT = 4*7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_cross_chain_messenger_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'messenger',
                                     'CrossChainMessenger.sol', 'CrossChainMessenger.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class ObscuroBridge:
    GAS_LIMIT = 4*7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_bridge_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'bridge', 'L1', 'ObscuroBridge.sol',
                                     'ObscuroBridge.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class EthereumBridge:
    GAS_LIMIT = 4*7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_bridge_address(test.env)
        self.abi_path =os.path.join(PROJECT.root, 'artifacts', 'contracts', 'bridge', 'L2', 'EthereumBridge.sol',
                                    'EthereumBridge.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class ObsERC20:
    GAS_LIMIT = 4*7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_bridge_address(test.env)
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'common', 'ObsERC20.sol', 'ObsERC20.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class WrappedERC20:
    GAS_LIMIT = 4*7200000

    def __init__(self, test, web3, name, symbol, address):
        self.test = test
        self.web3 = web3
        self.name = name
        self.symbol = symbol
        self.address = address
        self.abi_path = os.path.join(PROJECT.root, 'artifacts', 'contracts', 'common', 'WrappedERC20.sol',
                                     'WrappedERC20.json')
        with open(self.abi_path, 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)