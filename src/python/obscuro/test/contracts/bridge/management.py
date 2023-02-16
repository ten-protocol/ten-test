import os.path, json
from pysys.constants import *
from obscuro.test.utils.properties import Properties


class Management:
    """Abstraction over the pre-deployed L1 Management Contract."""
    GAS_LIMIT = 7200000

    def __init__(self, test, web3):
        """Construct an instance of the web3 contract class for the L1 management contract. """
        self.test = test
        self.web3 = web3
        self.address = Properties().l1_bridge_address(test.env)
        with open(os.path.join(PROJECT.root, 'artifacts', 'contracts', 'management', 'ManagementContract.sol',
                               'ManagementContract.json'), 'r') as fp:
            self.abi = json.load(fp)
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)

