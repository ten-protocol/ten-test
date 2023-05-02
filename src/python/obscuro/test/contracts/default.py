import json
from solcx import compile_source
from pysys.constants import *
from obscuro.test.utils.properties import Properties


class DefaultContract:
    GAS_LIMIT = 720000     # used as the max gas units prepared to pay in contract transactions
    SOURCE = None          # full path to the solidity source file
    CONTRACT = None        # the contract name

    def __init__(self, test, web3, *args):
        """Create an instance of the abstraction."""
        self.test = test
        self.web3 = web3
        self.bytecode = None
        self.abi = None
        self.abi_path = None
        self.contract = None
        self.address = None
        self.account = None
        self.args = args
        self.construct()

    def construct(self):
        """Compile and construct contract instance. """
        with open(self.SOURCE, 'r') as fp:
            compiled_sol = compile_source(source=fp.read(), output_values=['abi', 'bin'],
                                          solc_binary=Properties().solc_binary(),
                                          base_path=os.path.dirname(self.SOURCE))
            contract_interface = compiled_sol['<stdin>:%s' % self.CONTRACT]
            self.bytecode = contract_interface['bin']
            self.abi = contract_interface['abi']

        self.abi_path = os.path.join(self.test.output, '%s.abi' % self.CONTRACT)
        with open(self.abi_path, 'w') as f: json.dump(self.abi, f)

        self.contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode).constructor(*self.args)

    def deploy(self, network, account, persist_nonce=True):
        """Deploy using the given account."""
        self.test.log.info('Deploying the %s contract' % self.CONTRACT)
        self.account = account
        tx_receipt = network.transact(self.test, self.web3, self.contract, account, self.GAS_LIMIT, persist_nonce)
        self.address = tx_receipt.contractAddress
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)
        return tx_receipt
