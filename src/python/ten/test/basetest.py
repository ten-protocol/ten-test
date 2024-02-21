import os, copy, sys, json
import threading, requests
from web3 import Web3
from pathlib import Path
from pysys.basetest import BaseTest
from pysys.constants import PROJECT, BACKGROUND
from pysys.constants import LOG_TRACEBACK
from pysys.utils.logutils import BaseLogFormatter
from ten.test.persistence.nonce import NoncePersistence
from ten.test.persistence.funds import FundsPersistence
from ten.test.persistence.contract import ContractPersistence
from ten.test.utils.properties import Properties
from ten.test.networks.default import DefaultPostLondon
from ten.test.networks.ganache import Ganache
from ten.test.networks.goerli import Goerli
from ten.test.networks.arbitrum import ArbitrumSepolia
from ten.test.networks.sepolia import Sepolia
from ten.test.networks.ten import Ten
from ten.test.networks.ten import TenL1Geth, TenL1Sepolia


class GenericNetworkTest(BaseTest):
    """The base test used by all tests cases, against any request environment. """
    MSG_ID = 1                      # global used for http message requests numbers
    NODE_HOST = None                # if not none overrides the node host from the properties file

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to ten if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.env = self.mode
        self.block_time = Properties().block_time_secs(self.env)
        self.log.info('Running test in thread %s', threading.currentThread().getName())

        # every test has its own connection to the nonce and contract db
        db_dir = os.path.join(str(Path.home()), '.tentest')
        self.nonce_db = NoncePersistence(db_dir)
        self.contract_db = ContractPersistence(db_dir)
        self.funds_db = FundsPersistence(db_dir)
        self.addCleanupFunction(self.close_db)

        # every test has a connection for the funded account
        self.connections = {}
        self.network_funding = self.get_network_connection(name='funding')
        self.balance = 0
        self.accounts = []
        self.transfer_costs = []

        for fn in Properties().accounts():
            web3, account = self.network_funding.connect(self, fn(), check_funds=False, verbose=False)
            self.accounts.append((web3, account))
            self.balance = self.balance + web3.eth.get_balance(account.address)
        self.addCleanupFunction(self.__test_cost)

    def __test_cost(self):
        balance = 0
        for web3, account in self.accounts: balance = balance + web3.eth.get_balance(account.address)
        delta = abs(self.balance - balance)
        sign = '-' if (self.balance - balance) < 0 else ''
        self.log.info("  %s: %s%d Wei", 'Test cost', sign, delta, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
        self.log.info("  %s: %s%.9f ETH", 'Test cost', sign, Web3().from_wei(delta, 'ether'), extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))

    def close_db(self):
        """Close the connection to the nonce database on completion. """
        self.nonce_db.close()
        self.contract_db.close()

    def is_ten(self):
        """Return true if we are running against a Ten network. """
        return self.env in ['ten.sepolia', 'ten.uat', 'ten.dev', 'ten.local']

    def is_local_ten(self):
        """Return true if we are running against a local Ten network. """
        return self.env in ['ten.local']

    def is_sepolia_ten(self):
        """Return true if we are running against a sepolia Ten network. """
        return self.env in ['ten.sepolia']

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

    def run_npm(self, stdout, stderr, args, working_dir, timeout=120):
        self.log.info('Running npm with args "%s"', ' '.join(args))
        arguments = []
        if args is not None: arguments.extend(args)

        stdout = os.path.join(self.output, stdout)
        stderr = os.path.join(self.output, stderr)
        environ = copy.deepcopy(os.environ)
        self.startProcess(command=Properties().npm_binary(), displayName='npm', workingDir=working_dir,
                          arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                          timeout=timeout)

    def run_npx(self, stdout, stderr, args, environ, working_dir, timeout=120):
        self.log.info('Running npx with args "%s"', ' '.join(args))
        arguments = []
        if args is not None: arguments.extend(args)

        stdout = os.path.join(self.output, stdout)
        stderr = os.path.join(self.output, stderr)
        self.startProcess(command=Properties().npx_binary(), displayName='npm', workingDir=working_dir,
                          arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                          timeout=timeout)

    def distribute_native(self, account, amount, verbose=True):
        """A native transfer of funds from the funded account to another.

        Note that these methods are called from connect to perform a transfer. The account performing the transfer
        needs to also connect, hence to avoid recursion we don't check funds on the call.
        """
        web3_pk, account_pk = self.network_funding.connect(self, Properties().fundacntpk(), check_funds=False, verbose=verbose)
        balance_before = web3_pk.eth.get_balance(account_pk.address)

        tx = {'to': account.address, 'value': web3_pk.to_wei(amount, 'ether'), 'gasPrice': web3_pk.eth.gas_price}
        tx['gas'] = web3_pk.eth.estimate_gas(tx)
        if verbose: self.log.info('Gas estimate for distribute native is %d', tx['gas'])

        if verbose: self.log.info('Sending %.6f ETH to account %s', amount, account.address)
        self.network_funding.tx(self, web3_pk, tx, account_pk, verbose=verbose)
        balance_after = web3_pk.eth.get_balance(account_pk.address)
        self.transfer_costs.append((balance_before - web3_pk.to_wei(amount, 'ether') - balance_after))

    def drain_native(self, web3, account, network):
        """A native transfer of all funds from and account to the funded account."""
        average_cost = int(sum(self.transfer_costs) / len(self.transfer_costs))
        balance = web3.eth.get_balance(account.address)
        amount = web3.eth.get_balance(account.address) - 10*average_cost
        self.log.info("Drain account %s of %d (current balance %d)", account.address, amount, balance)

        address = Web3().eth.account.from_key(Properties().fundacntpk()).address
        self.log.info('Send to address is %s', address)

        tx = {'to':  address, 'value': amount, 'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        self.log.info('Gas estimate for drain native is %d', tx['gas'])
        network.tx(self, web3, tx, account, persist_nonce=False)

    def fund_native(self, network, account, amount, pk, persist_nonce=True, gas_limit=None):
        """A native transfer of funds from one address to another.

        Note that these methods are called from connect to perform a transfer. The account performing the transfer
        needs to also connect, hence to avoid recursion we don't check funds on the call.
        """
        web3_pk, account_pk = network.connect(self, pk, check_funds=False)

        tx = {'to': account.address, 'value': web3_pk.to_wei(amount, 'ether'), 'gasPrice': web3_pk.eth.gas_price}
        if gas_limit is not None: tx['gas'] = gas_limit
        else: tx['gas'] = web3_pk.eth.estimate_gas(tx)
        self.log.info('Gas estimate for fund native is %d', tx['gas'])
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

    def get_network_connection(self, name='primary', **kwargs):
        """Get the network connection."""
        if self.is_ten():
            return Ten(self, name, **kwargs)
        elif self.env == 'goerli':
            return Goerli(self, name, **kwargs)
        elif self.env == 'ganache':
            return Ganache(self, name, **kwargs)
        elif self.env == 'arbitrum.sepolia':
            return ArbitrumSepolia(self, name, **kwargs)
        elif self.env == 'sepolia':
            return Sepolia(self, name, **kwargs)

        return DefaultPostLondon(self, name, **kwargs)

    def get_l1_network_connection(self, name='primary_l1_connection', **kwargs):
        """Get the layer 1 network connection used by a layer 2."""
        if self.is_ten() and self.env != 'ten.sepolia':
            return TenL1Geth(self, name, **kwargs)
        elif self.is_ten() and self.env == 'ten.sepolia':
            return TenL1Sepolia(self, name, **kwargs)
        return DefaultPostLondon(self, name, **kwargs)


class TenNetworkTest(GenericNetworkTest):
    """The test used by all Ten specific network testcases.

    Test class specific for the Ten Network. Provides utilities for funding native ETH and ERC20 tokens in the layer1 and
    layer2 of an Ten Network.
    """

    def tenscan_get_total_transactions(self):
        """Return the total number of L2 transactions on Ten. """
        data = {"jsonrpc": "2.0", "method": "tenscan_getTotalTransactions", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return int(response.json()['result'])
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def tenscan_get_latest_transactions(self, num):
        """Return the last x number of L2 transactions. """
        data = {"jsonrpc": "2.0", "method": "tenscan_getLatestTransactions", "params": [num], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def tenscan_get_head_rollup_header(self):
        """Get the rollup header of the head rollup. """
        data = {"jsonrpc": "2.0", "method": "tenscan_getHeadRollupHeader", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def tenscan_get_batch(self, hash):
        """Get the rollup by its hash. """
        data = {"jsonrpc": "2.0", "method": "tenscan_getBatch", "params": [hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def tenscan_get_batch_for_transaction(self, tx_hash):
        """Get the rollup for a given L2 transaction. """
        data = {"jsonrpc": "2.0", "method": "tenscan_getBatchForTx", "params": [tx_hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def tenscan_get_l1_block(self, block_hash):
        """Get the block that contains a given rollup (given by the L1Proof value in the header). """
        data = {"jsonrpc": "2.0", "method": "tenscan_getBlockHeaderByHash", "params": [block_hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def tenscan_get_node_attestation(self):
        """Get the node attestation report. """
        data = {"jsonrpc": "2.0", "method": "tenscan_attestation", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def get_debug_event_log_relevancy(self, tx_hash):
        """Get the debug_LogVisibility. """
        data = {"jsonrpc": "2.0", "method": "debug_eventLogRelevancy", "params": [tx_hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_latest_rollup_header(self):
        """Get the latest rollup header as part of the scan_ api."""
        data = {"jsonrpc": "2.0", "method": "scan_getLatestRollupHeader", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_total_transaction_count(self):
        """Get the ltotal transaction count as part of the scan_ api."""
        data = {"jsonrpc": "2.0", "method": "scan_getTotalTransactionCount", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_total_contract_count(self):
        """Get the total contract count as part of the scan_ api."""
        data = {"jsonrpc": "2.0", "method": "scan_getTotalContractCount", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_public_transaction_data(self, offset=0, size=10):
        """Get the public transaction data as part of the scan_ api."""
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getPublicTransactionData", "params": [pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_batch_listing(self, offset=0, size=10):
        """Get the batch listing as part of the scan_ api."""
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getBatchListing", "params": [pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_block_listing(self, offset=0, size=10):
        """Get the block listing as part of the scan_ api."""
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getBlockListing", "params": [pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_batch_by_hash(self, hash):
        """Get block by hash as part of the scan_ api."""
        data = {"jsonrpc": "2.0", "method": "scan_getBatchByHash", "params": [hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_list_personal_transactions(self, address, offset=0, size=10):
        """List personal transactions using ."""
        payload = {
            "address": address,
            "pagination": {"offset": offset, "size": size},
        }
        data = {"jsonrpc": "2.0", "method": "eth_getStorageAt", "params": ["listPersonalTransactions", payload, None], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def obscuro_health(self):
        """Get the debug_LogVisibility. """
        data = {"jsonrpc": "2.0", "method": "obscuro_health", "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def obscuro_config(self):
        """Get the obscuro_config. """
        data = {"jsonrpc": "2.0", "method": "obscuro_config", "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def post(self, data):
        self.MSG_ID += 1
        server = 'http://%s:%s' % (Properties().node_host(self.env, self.NODE_HOST), Properties().node_port_http(self.env))
        return requests.post(server, json=data)
