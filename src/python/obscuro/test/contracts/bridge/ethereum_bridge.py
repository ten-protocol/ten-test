import os.path, json
from pysys.constants import *
from obscuro.test.utils.properties import Properties


class EthereumBridge:
    """Abstraction over the pre-deployed L2 Ethereum Bridge."""

    def __init__(self, test, web3):
        """Construct an instance of the web3 contract class for the L2 bridge contract. """
        self.test = test
        self.web3 = web3
        self.contract_address = Properties().l2_bridge_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'bridge', 'L2', 'EthereumBridge.sol',
                                  'EthereumBridge.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.abi)
