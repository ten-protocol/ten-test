import json
from copy import copy
from solcx import compile_source
from pysys.constants import *
from pysys.constants import LOG_WARN
from pysys.utils.logutils import BaseLogFormatter
from ten.test.utils.properties import Properties


class DefaultContract:
    GAS_LIMIT = 3_000_000  # used as the max gas units prepared to pay in contract transactions
    SOURCE = None          # full path to the solidity source file
    CONTRACT = None        # the contract name

    @classmethod
    def clone(cls, web3, account, contract):
        clone = copy(contract)
        clone.web3 = web3
        clone.account = account
        clone.contract = web3.eth.contract(address=contract.address, abi=contract.abi)
        return clone

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

    def deploy(self, network, account, persist_nonce=True, timeout=30):
        """Deploy using the given account."""
        self.test.log.info('Deploying %s contract', self.CONTRACT, extra=BaseLogFormatter.tag(LOG_WARN, 0))
        self.account = account
        tx_receipt = network.transact(self.test, self.web3, self.contract, account,
                                      self.GAS_LIMIT, persist_nonce, timeout=timeout)
        self.address = tx_receipt.contractAddress
        self.contract = self.web3.eth.contract(address=self.address, abi=self.abi)
        self.test.log.info('Contract %s deployed at %s', self.CONTRACT, tx_receipt.contractAddress, extra=BaseLogFormatter.tag(LOG_WARN, 0))
        return tx_receipt

    def get_or_deploy(self, network, account, persist_nonce=True, timeout=30):
        """Get the contract from persistence, or deploy if it is not there. """
        address, abi = self.test.contract_db.get_contract(self.CONTRACT, self.test.env)
        if address is not None:
            self.test.log.info('Using pre-deployed contract at address %s', address)
            if self.web3.eth.get_code(address) == b'':
                self.test.log.warn('Contract address does not appear to be a deployed contract ... deploying')
                self.deploy(network, account, persist_nonce=persist_nonce, timeout=timeout)
                self.test.contract_db.insert_contract(self.CONTRACT, self.test.env, self.address, json.dumps(self.abi))
            else:
                self.address = address
                self.contract = self.web3.eth.contract(address=address, abi=abi)
        else:
            self.test.log.warn('Contract does not appear to be deployed ... deploying')
            self.deploy(network, account, persist_nonce=persist_nonce)
            self.test.contract_db.insert_contract(self.CONTRACT, self.test.env, self.address, json.dumps(self.abi))

    def set_persisted_param(self, key, value):
        """Persist a parameter value for this contract. """
        self.test.contract_db.insert_param(self.address, self.test.env, key, value)

    def get_persisted_param(self, key, default):
        """Get a persisted parameter for this contract, or return the default if it does not exist. """
        value = self.test.contract_db.get_param(self.address, self.test.env, key)
        return default if value is None else value