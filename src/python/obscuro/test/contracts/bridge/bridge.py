import os.path, json
from pysys.constants import *
from obscuro.test.utils.properties import Properties


class ObscuroBridge:
    """Abstraction over the pre-deployed L1 Obscuro Bridge."""
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        """Construct an instance of the web3 contract class for the L1 bridge contract. """
        self.test = test
        self.web3 = web3
        self.contract_address = Properties().l1_bridge_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'bridge', 'L1', 'ObscuroBridge.sol',
                               'ObscuroBridge.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.abi)


class EthereumBridge:
    """Abstraction over the pre-deployed L2 Ethereum Bridge."""
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        """Construct an instance of the web3 contract class for the L2 bridge contract. """
        self.test = test
        self.web3 = web3
        self.contract_address = Properties().l2_bridge_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'bridge', 'L2', 'EthereumBridge.sol',
                                  'EthereumBridge.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.abi)
