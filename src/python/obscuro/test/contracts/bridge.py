import os.path, json
from pysys.constants import *
from obscuro.test.utils.properties import Properties


class Management:
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_bridge_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'management', 'ManagementContract.sol',
                               'ManagementContract.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L1MessageBus:
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_message_bus_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'MessageBus.sol',
                               'MessageBus.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L2MessageBus:
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_message_bus_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'MessageBus.sol',
                               'MessageBus.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class CrossChainMessenger:
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_cross_chain_messenger_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'messenger',
                               'CrossChainMessenger.sol', 'CrossChainMessenger.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class ObscuroBridge:
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_bridge_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'bridge', 'L1', 'ObscuroBridge.sol',
                               'ObscuroBridge.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class EthereumBridge:
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_bridge_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'bridge', 'L2', 'EthereumBridge.sol',
                                  'EthereumBridge.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


