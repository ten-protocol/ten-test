import json
from pysys.constants import *
from solcx import compile_source
from obscuro.test.utils.process import Processes


class OBXCoin:
    """Abstraction over the ERC20 smart contract used locally."""
    GAS = 7200000

    def __init__(self, test, web3):
        """Create an instance of the ERC20 contract, compile and construct a web3 instance. """
        self.bytecode = None
        self.abi = None
        self.abi_path = None
        self.contract = None
        self.contract_address = None
        self.account = None
        self.test = test
        self.web3 = web3
        self.construct()

    def construct(self):
        """Compile and construct an instance."""
        file = os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'OBXCoin.sol')
        with open(file, 'r') as fp:
            compiled_sol = compile_source(source=fp.read(), output_values=['abi', 'bin'],
                                          solc_binary=Processes.get_solidity_compiler(),
                                          base_path=os.path.dirname(file))
            contract_interface = compiled_sol['<stdin>:OBXCoin']
            self.bytecode = contract_interface['bin']
            self.abi = contract_interface['abi']

        self.abi_path = os.path.join(self.test.output, 'obx.abi')
        with open(self.abi_path, 'w') as f: json.dump(self.abi, f)

        self.contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode).constructor()

    def deploy(self, network, account):
        """Deploy the contract using a given account."""
        self.account = account
        tx_receipt = network.transact(self.test, self.web3, self.contract, account, self.GAS)
        self.contract_address = tx_receipt.contractAddress
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.abi)
        return tx_receipt
