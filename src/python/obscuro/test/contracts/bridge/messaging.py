import os.path, json
from pysys.constants import *
from obscuro.test.utils.properties import Properties


class L1MessageBus:
    """Abstraction over the pre-deployed L1 Message Bus."""
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        """Contract an instance of the web3 contract class for the L2 bridge contract. """
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_message_bus_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'MessageBus.sol',
                                  'MessageBus.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class L2MessageBus:
    """Abstraction over the pre-deployed L2 Message Bus."""
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        """Contract an instance of the web3 contract class for the L2 bridge contract. """
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_message_bus_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'MessageBus.sol',
                               'MessageBus.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)


class CrossChainMessenger:
    """Abstraction over the pre-deployed L2 Cross Chain Messenger."""
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        """Contract an instance of the web3 contract class for the L2 cross chain messenger."""
        self.test = test
        self.web3 = web3
        self.address = Properties().l2_cross_chain_messenger_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'messaging', 'messenger',
                               'CrossChainMessenger.sol', 'CrossChainMessenger.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

