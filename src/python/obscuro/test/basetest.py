import os, copy, sys, json
import threading, requests, secrets
from web3 import Web3
from pathlib import Path
from pysys.basetest import BaseTest
from pysys.constants import PROJECT, BACKGROUND
from pysys.constants import LOG_TRACEBACK
from pysys.utils.logutils import BaseLogFormatter
from obscuro.test.persistence.nonce import NoncePersistence
from obscuro.test.persistence.contract import ContractPersistence
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import Default
from obscuro.test.networks.ganache import Ganache
from obscuro.test.networks.goerli import Goerli
from obscuro.test.networks.arbitrum import Arbitrum
from obscuro.test.networks.sepolia import Sepolia
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.networks.obscuro import ObscuroL1Geth, ObscuroL1Sepolia


class GenericNetworkTest(BaseTest):
    """The base test used by all tests cases, against any request environment. """
    MSG_ID = 1                      # global used for http message requests numbers
    NODE_HOST = None                # if not none overrides the node host from the properties file

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to obscuro if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.env = self.mode
        self.block_time = Properties().block_time_secs(self.env)
        self.log.info('Running test in thread %s', threading.currentThread().getName())

        # every test has its own connection to the nonce and contract db
        db_dir = os.path.join(str(Path.home()), '.obscurotest')
        self.nonce_db = NoncePersistence(db_dir)
        self.contract_db = ContractPersistence(db_dir)
        self.addCleanupFunction(self.close_db)

        # every test has a connection for the funded account
        self.network_funding = self.get_network_connection(name='funding_connection')
        self.balance = 0
        self.accounts = []
        self.transfer_costs = []

        for fn in Properties().accounts():
            web3, account = self.network_funding.connect(self, fn(), check_funds=False, log=False)
            self.accounts.append((web3, account))
            self.balance = self.balance + web3.eth.get_balance(account.address)
        self.addCleanupFunction(self.__test_cost)

    def __test_cost(self):
        balance = 0
        for web3, account in self.accounts: balance = balance + web3.eth.get_balance(account.address)
        delta = self.balance - balance
        self.log.info("  %s: %d Wei", 'Test cost', delta, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
        self.log.info("  %s: %.9f ETH", 'Test cost', Web3().fromWei(delta, 'ether'), extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))

    def close_db(self):
        """Close the connection to the nonce database on completion. """
        self.nonce_db.close()
        self.contract_db.close()

    def is_obscuro(self):
        """Return true if we are running against an Obscuro network. """
        return self.env in ['obscuro', 'obscuro.sepolia', 'obscuro.dev', 'obscuro.local']

    def is_local_obscuro(self):
        """Return true if we are running against a local Obscuro network. """
        return self.env in ['obscuro.local']

    def run_python(self, script, stdout, stderr, args=None, state=BACKGROUND, timeout=120):
        """Run a python process. """
        self.log.info('Running python script %s', os.path.basename(script))
        arguments = [script]
        if args is not None: arguments.extend(args)

        environ = copy.deepcopy(os.environ)
        hprocess = self.startProcess(command=sys.executable, displayName='python', workingDir=self.output,
                                     arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                                     state=state, timeout=timeout)
        return hprocess

    def run_javascript(self, script, stdout, stderr, args=None, state=BACKGROUND, timeout=120):
        """Run a javascript process. """
        self.log.info('Running javascript %s', os.path.basename(script))
        arguments = [script]
        if args is not None: arguments.extend(args)

        environ = copy.deepcopy(os.environ)
        node_path = '%s:%s' % (Properties().node_path(), os.path.join(PROJECT.root, 'src', 'javascript', 'modules'))
        if "NODE_PATH" in environ:
            environ["NODE_PATH"] = node_path + ":" + environ["NODE_PATH"]
        else:
            environ["NODE_PATH"] = node_path
        hprocess = self.startProcess(command=Properties().node_binary(), displayName='node', workingDir=self.output,
                                     arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                                     state=state, timeout=timeout)
        return hprocess

    def distribute_native(self, account, amount):
        """A native transfer of funds from the funded account to another.

        Note that these methods are called from connect to perform a transfer. The account performing the transfer
        needs to also connect, hence to avoid recursion we don't check funds on the call.
        """
        web3_pk, account_pk = self.network_funding.connect(self, Properties().fundacntpk(), check_funds=False)

        tx = {
            'to': account.address,
            'value': web3_pk.toWei(amount, 'ether'),
            'gas': 4*21000,
            'gasPrice': web3_pk.eth.gas_price
        }

        balance_before = web3_pk.eth.get_balance(account_pk.address)
        self.network_funding.tx(self, web3_pk, tx, account_pk)
        balance_after = web3_pk.eth.get_balance(account_pk.address)
        self.transfer_costs.append((balance_before - web3_pk.toWei(amount, 'ether') - balance_after))
        average = (sum(self.transfer_costs) / len(self.transfer_costs))
        self.log.info("Average cost for a transfer is %d", average)
        self.log.info("Funds for %s: %.18f ETH", "fundacntpk ", Web3().fromWei(balance_after, 'ether'),
                      extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))

    def drain_native(self, web3, account, network):
        """A native transfer of all funds from and account to the funded account."""
        average_cost = int(sum(self.transfer_costs) / len(self.transfer_costs))
        balance = web3.eth.get_balance(account.address)
        amount = web3.eth.get_balance(account.address) - 10*average_cost
        self.log.info("Drain account %s of %d (current balance %d)", account.address, amount, balance)

        address = Web3().eth.account.privateKeyToAccount(Properties().fundacntpk()).address
        self.log.info('Send to address is %s', address)
        tx = {
            'to':  address,
            'value': amount,
            'gas': 4*21000,
            'gasPrice': web3.eth.gas_price
        }
        network.tx(self, web3, tx, account, persist_nonce=False)

    def fund_native(self, network, account, amount, pk, persist_nonce=True):
        """A native transfer of funds from one address to another.

        Note that these methods are called from connect to perform a transfer. The account performing the transfer
        needs to also connect, hence to avoid recursion we don't check funds on the call.
        """
        web3_pk, account_pk = network.connect(self, pk, check_funds=False)
        tx = {
            'to': account.address,
            'value': web3_pk.toWei(amount, 'ether'),
            'gas': 4*21000,
            'gasPrice': web3_pk.eth.gas_price
        }
        network.tx(self, web3_pk, tx, account_pk, persist_nonce=persist_nonce)

    def transfer_token(self, network, token_name, token_address, web3_from, account_from, address,
                       amount, persist_nonce=True):
        """Transfer an ERC20 token amount from a recipient account to an address. """
        self.log.info('Running for token %s', token_name)

        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3_from.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account_from.address).call({"from":account_from.address})
        self.log.info('%s User balance   = %d ', token_name, balance)
        network.transact(self, web3_from, token.functions.transfer(address, amount), account_from, 7200000, persist_nonce)

        balance = token.functions.balanceOf(account_from.address).call({"from":account_from.address})
        self.log.info('%s User balance   = %d ', token_name, balance)

    def print_token_balance(self, token_name, token_address, web3, account):
        """Print an ERC20 token balance of a recipient account. """
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account.address).call()
        self.log.info('%s User balance   = %d ', token_name, balance)

    def get_token_balance(self, token_address, web3, account):
        """Get the ERC20 token balance of a recipient account. """
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3.eth.contract(address=token_address, abi=json.load(f))
        return token.functions.balanceOf(account.address).call()

    def get_network_connection(self, name='primary_connection', **kwargs):
        """Get the network connection."""
        if self.is_obscuro():
            print("is obscuro..")
            return Obscuro(self, name, **kwargs)
        elif self.env == 'goerli':
            return Goerli(self, name, **kwargs)
        elif self.env == 'ganache':
            return Ganache(self, name, **kwargs)
        elif self.env == 'arbitrum':
            return Arbitrum(self, name, **kwargs)
        elif self.env == 'sepolia':
            return Sepolia(self, name, **kwargs)

        return Default(self, name, **kwargs)

    def get_l1_network_connection(self, name='primary_l1_connection'):
        """Get the layer 1 network connection used by a layer 2."""
        if self.is_obscuro() and self.env != 'obscuro.sepolia':
            return ObscuroL1Geth(self, name)
        elif self.is_obscuro() and self.env == 'obscuro.sepolia':
            return ObscuroL1Sepolia(self, name)
        return Default(self, name)


class ObscuroNetworkTest(GenericNetworkTest):
    """The test used by all Obscuro specific network testcases.

    Test class specific for the Obscuro Network. Provides utilities for funding OBX and ERC20 tokens in the layer1 and
    layer2 of an Obscuro Network.
    """

    def get_total_transactions(self):
        """Return the total number of L2 transactions on Obscuro. """
        data = {"jsonrpc": "2.0", "method": "obscuroscan_getTotalTransactions", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return int(response.json()['result'])
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def get_latest_transactions(self, num):
        """Return the last x number of L2 transactions. """
        data = {"jsonrpc": "2.0", "method": "obscuroscan_getLatestTransactions", "params": [num], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def get_head_rollup_header(self):
        """Get the rollup header of the head rollup. """
        data = {"jsonrpc": "2.0", "method": "obscuroscan_getHeadRollupHeader", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def get_batch(self, hash):
        """Get the rollup by its hash. """
        data = {"jsonrpc": "2.0", "method": "obscuroscan_getBatch", "params": [hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def get_batch_for_transaction(self, tx_hash):
        """Get the rollup for a given L2 transaction. """
        data = {"jsonrpc": "2.0", "method": "obscuroscan_getBatchForTx", "params": [tx_hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def get_l1_block(self, block_hash):
        """Get the block that contains a given rollup (given by the L1Proof value in the header). """
        data = {"jsonrpc": "2.0", "method": "obscuroscan_getBlockHeaderByHash", "params": [block_hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def get_node_attestation(self):
        """Get the node attestation report. """
        data = {"jsonrpc": "2.0", "method": "obscuroscan_attestation", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def get_debug_log_visibility(self, tx_hash):
        """Get the debug_LogVisibility. """
        data = {"jsonrpc": "2.0", "method": "debug_eventLogRelevancy", "params": [tx_hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def post(self, data):
        self.MSG_ID += 1
        server = 'http://%s:%s' % (Properties().node_host(self.env, self.NODE_HOST), Properties().node_port_http(self.env))
        return requests.post(server, json=data)
