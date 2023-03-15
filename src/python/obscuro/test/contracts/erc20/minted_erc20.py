import json
from pysys.constants import *
from solcx import compile_source
from obscuro.test.utils.properties import Properties


class MintedERC20Token:
    """Abstraction over the ERC20 smart contract used locally."""
    GAS_LIMIT = 7200000

    def __init__(self, test, web3, name, symbol, supply):
        """Create an instance of the abstraction."""
        self.bytecode = None
        self.abi = None
        self.abi_path = None
        self.contract = None
        self.address = None
        self.account = None
        self.test = test
        self.web3 = web3
        self.name = name
        self.symbol = symbol
        self.supply = supply
        self.construct()

    def construct(self):
        """Compile and construct an instance."""
        file = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'MintedERC20.sol')
        with open(file, 'r') as fp:
            compiled_sol = compile_source(source=fp.read(), output_values=['abi', 'bin'],
                                          solc_binary=Properties().solc_binary(),
                                          base_path=os.path.dirname(file))
            contract_interface = compiled_sol['<stdin>:MintedERC20']
            self.bytecode = contract_interface['bin']
            self.abi = contract_interface['abi']

        self.abi_path = os.path.join(self.test.output, 'erc20.abi')
        with open(self.abi_path, 'w') as f: json.dump(self.abi, f)

        self.contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode).constructor(self.name, self.symbol, self.supply)

    def deploy(self, network, account, persist_nonce=True):
        """Deploy the contract using a given account."""
        self.account = account
        tx_receipt = network.transact(self.test, self.web3, self.contract, account, self.GAS_LIMIT, persist_nonce=persist_nonce)
        self.address = tx_receipt.contractAddress
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)
        return tx_receipt
