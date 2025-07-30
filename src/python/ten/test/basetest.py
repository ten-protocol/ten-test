import os, copy, sys, json
import time, secrets, re
import threading, requests
from web3 import Web3
from pysys.basetest import BaseTest
from pysys.constants import PROJECT, BACKGROUND, FAILED, TIMEDOUT
from pysys.constants import LOG_TRACEBACK
from pysys.utils.logutils import BaseLogFormatter
from ten.test.persistence.rates import RatesPersistence
from ten.test.persistence.nonce import NoncePersistence
from ten.test.persistence.counts import CountsPersistence
from ten.test.persistence.stats import StatsPersistence
from ten.test.persistence.funds import FundsPersistence, PandLPersistence, GasPricePersistence
from ten.test.persistence.results import PerformanceResultsPersistence, TxCostResultsPersistence, RunTypePersistence
from ten.test.persistence.contract import ContractPersistence
from ten.test.utils.properties import Properties
from ten.test.networks.default import DefaultPostLondon
from ten.test.networks.ganache import Ganache
from ten.test.networks.goerli import Goerli
from ten.test.networks.sepolia import Sepolia
from ten.test.networks.optimism import OptimismSepolia, OptimismL1Sepolia
from ten.test.networks.arbitrum import ArbitrumSepolia, ArbitrumL1Sepolia
from ten.test.networks.ten import Ten, TenL1Geth, TenL1Sepolia


class GenericNetworkTest(BaseTest):
    """The base test used by all tests cases, against any request environment. """
    MSG_ID = 1                      # global used for http message requests numbers
    PERSIST_PERF = False            # if true persist performance results to the db

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to ten if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.env = self.mode
        self.block_time = Properties().block_time_secs(self.env)
        self.log.info('Running test in thread %s', threading.currentThread().getName())
        self.user_dir = runner.ten_runner.user_dir
        self.machine_name = runner.ten_runner.machine_name
        self.is_cloud_vm = runner.ten_runner.is_cloud_vm
        if hasattr(runner, 'uuid'): self.log.info('Running as job uuid %s', runner.uuid)

        # every test has its own connection to the dbs - use a remote mysql persistence layer if we are running in
        # azure, and it is not a local testnet. The exception for this is the nonce db where it is always local.
        use_remote = (not self.is_local_ten() and self.is_cloud_vm)
        self.rates_db = RatesPersistence(use_remote, self.user_dir, self.machine_name)
        self.nonce_db = NoncePersistence(use_remote, self.user_dir, self.machine_name)
        self.contract_db = ContractPersistence(use_remote, self.user_dir, self.machine_name)
        self.funds_db = FundsPersistence(use_remote, self.user_dir, self.machine_name)
        self.pandl_db = PandLPersistence(use_remote, self.user_dir, self.machine_name)
        self.gas_db = GasPricePersistence(use_remote, self.user_dir, self.machine_name)
        self.counts_db = CountsPersistence(use_remote, self.user_dir, self.machine_name)
        self.results_db = PerformanceResultsPersistence(self.is_cloud_vm, self.user_dir, self.machine_name)
        self.txcosts_db = TxCostResultsPersistence(use_remote, self.user_dir, self.machine_name)
        self.runtype_db = RunTypePersistence.init(use_remote, self.user_dir, self.machine_name)
        self.stats_db = StatsPersistence(True, self.user_dir, self.machine_name)
        self.addCleanupFunction(self.close_db)

        # every test has a unique connection for the funded account
        self.network_funding = None
        self.connections = {}
        self.balance = 0
        self.accounts = []
        self.ephemeral_pks = []
        self.transfer_costs = []
        self.average_transfer_cost = 21000000000000
        self.cost = 0
        _, self.eth_price = self.rates_db.get_latest_rate('ETH', 'USD')

        if runner.xargs.get('NO_CONNECT', False):
            runner.log.warn('No connection to the network has been requested for this test run')

        else:
            self.network_funding = self.get_network_connection()
            for fn in Properties().accounts():
                web3, account = self.network_funding.connect(self, fn(), check_funds=False, verbose=False)
                self.accounts.append((web3, account))
                self.balance = self.balance + web3.eth.get_balance(account.address)
            self.addCleanupFunction(self.__test_cost)
            self.addCleanupFunction(self.drain_ephemeral_pks)

    def __test_cost(self):
        balance = 0
        for web3, account in self.accounts: balance = balance + web3.eth.get_balance(account.address)
        delta = abs(self.balance - balance)
        sign = '-' if (self.balance - balance) < 0 else ''
        self.log.info("  %s: %s%d WEI", 'Test cost', sign, delta, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
        self.log.info("  %s: %s%.9f ETH", 'Test cost', sign, Web3().from_wei(delta, 'ether'), extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))
        if self.eth_price is not None:
            self.cost = round(self.eth_price*float(Web3().from_wei(delta, 'ether')), 3)
            if (self.balance - balance) < 0: self.cost = 0
            change = float(Web3().from_wei(delta, 'ether'))
            self.log.info("  %s: %s%.3f USD", 'Test cost', sign, self.eth_price*change, extra=BaseLogFormatter.tag(LOG_TRACEBACK, 0))

    def close_db(self):
        """Close the connection to the databases on completion. """
        self.rates_db.close()
        self.nonce_db.close()
        self.contract_db.close()
        self.funds_db.close()
        self.pandl_db.close()
        self.gas_db.close()
        self.counts_db.close()
        self.results_db.close()
        self.txcosts_db.close()
        self.runtype_db.close()
        self.stats_db.close()

    def drain_ephemeral_pks(self):
        """Drain any ephemeral accounts of their funds. """
        if len(self.ephemeral_pks) == 0: return
        for pk in self.ephemeral_pks:
            web3, account = self.network_funding.connect(self, private_key=pk, check_funds=False, verbose=False)
            self.drain_native(web3, account, self.network_funding)
        self.log.info('')

    def is_ten(self):
        """Return true if we are running against a Ten network. """
        return self.env in ['ten.sepolia', 'ten.uat', 'ten.dev', 'ten.local', 'ten.sim']

    def is_local_ten(self):
        """Return true if we are running against a local Ten network. """
        return self.env in ['ten.local']

    def is_sepolia_ten(self):
        """Return true if we are running against a sepolia Ten network. """
        return self.env in ['ten.sepolia']

    def get_ephemeral_pk(self):
        private_key = secrets.token_hex(32)
        self.ephemeral_pks.append(private_key)
        return private_key

    def run_python(self, script, stdout, stderr, args=None, workingDir=None, state=BACKGROUND, timeout=120):
        """Run a python process. """
        self.log.info('Running python script %s', os.path.basename(script))
        arguments = [script]
        if args is not None: arguments.extend(args)
        if workingDir is None: workingDir = self.output

        environ = copy.deepcopy(os.environ)
        hprocess = self.startProcess(command=sys.executable, displayName='python', workingDir=workingDir,
                                     arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                                     state=state, timeout=timeout)
        return hprocess

    def run_javascript(self, script, stdout, stderr, args=None, workingDir=None, state=BACKGROUND, timeout=120):
        """Run a javascript process. """
        self.log.info('Running javascript %s', os.path.basename(script))
        arguments = [script]
        if args is not None: arguments.extend(args)
        if workingDir is None: workingDir = self.output

        environ = copy.deepcopy(os.environ)
        node_path = '%s:%s' % (Properties().node_path(), os.path.join(PROJECT.root, 'src', 'javascript', 'modules'))
        if "NODE_PATH" in environ:
            environ["NODE_PATH"] = node_path + ":" + environ["NODE_PATH"]
        else:
            environ["NODE_PATH"] = node_path
        hprocess = self.startProcess(command=Properties().node_binary(), displayName='node', workingDir=workingDir,
                                     arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                                     state=state, timeout=timeout)
        return hprocess

    def run_npm(self, stdout, stderr, args, working_dir, timeout=180):
        self.log.info('Running npm with args "%s"', ' '.join(args))
        arguments = []
        if args is not None: arguments.extend(args)

        stdout = os.path.join(self.output, stdout)
        stderr = os.path.join(self.output, stderr)
        environ = copy.deepcopy(os.environ)
        self.startProcess(command=Properties().npm_binary(), displayName='npm', workingDir=working_dir,
                          arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                          timeout=timeout)

    def run_npx(self, stdout, stderr, args, environ, working_dir, timeout=180):
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

        tx = {'to': account.address, 'value': web3_pk.to_wei(amount, 'ether'), 'gasPrice': web3_pk.eth.gas_price,
              'chainId': web3_pk.eth.chain_id}
        tx['gas'] = web3_pk.eth.estimate_gas(tx)
        if verbose: self.log.info('Gas supplied for distribute native is %d', tx['gas'])

        if verbose: self.log.info('Sending %.9f ETH to account %s', amount, account.address)
        self.network_funding.tx(self, web3_pk, tx, account_pk, verbose=verbose, txstr='value transfer')
        balance_after = web3_pk.eth.get_balance(account_pk.address)
        cost = balance_before - web3_pk.to_wei(amount, 'ether') - balance_after
        if cost < 21000*web3_pk.eth.gas_price: cost = 21000*web3_pk.eth.gas_price
        self.transfer_costs.append(cost)
        self.log.info('Average transfer cost: %.9f ETH' % web3_pk.from_wei(self.average_transfer_cost, 'ether'))

    def drain_native(self, web3, account, network):
        """A native transfer of all funds from an account to the funded account."""
        balance = web3.eth.get_balance(account.address)
        if balance == 0: return
        self.log.info("Draining account %s", account.address)
        if balance < self.average_transfer_cost:
            self.log.info('Drain estimate cost:  %.9f ETH' % web3.from_wei(self.average_transfer_cost, 'ether'))
            self.log.info('Pre-drain balance:    %.9f ETH' % web3.from_wei(balance, 'ether'))
            self.log.info('Post-drain balance:   %.9f ETH' % web3.from_wei(balance, 'ether'))
            return

        amount = web3.eth.get_balance(account.address) - self.average_transfer_cost
        tx = {'nonce': web3.eth.get_transaction_count(account.address),
              'chainId': web3.eth.chain_id,
              'to':  Web3().eth.account.from_key(Properties().fundacntpk()).address,
              'value': amount,
              'gasPrice': web3.eth.gas_price}
        tx['gas'] = web3.eth.estimate_gas(tx)
        tx['value'] = web3.eth.get_balance(account.address) - tx['gas'] * web3.eth.gas_price

        self.log.info('Drain estimate cost:  %.9f ETH' % web3.from_wei(tx['gas'] * web3.eth.gas_price, 'ether'))
        self.log.info('Pre-drain balance:    %.9f ETH' % web3.from_wei(web3.eth.get_balance(account.address), 'ether'))
        try:
            signed_tx = account.sign_transaction(tx)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            web3.eth.wait_for_transaction_receipt(tx_hash)
        except:
            pass # fail silently
        self.log.info('Post-drain balance:   %.9f ETH' % web3.from_wei(web3.eth.get_balance(account.address), 'ether'))

    def fund_native(self, network, account, amount, pk, persist_nonce=True, gas_limit=None):
        """A native transfer of funds from one address to another.

        Note that these methods are called from connect to perform a transfer. The account performing the transfer
        needs to also connect, hence to avoid recursion we don't check funds on the call.
        """
        web3_pk, account_pk = network.connect(self, pk, check_funds=False)

        tx = {'to': account.address, 'value': web3_pk.to_wei(amount, 'ether'), 'gasPrice': web3_pk.eth.gas_price, 'chainId': web3_pk.eth.chain_id}
        if gas_limit is not None: tx['gas'] = gas_limit
        else: tx['gas'] = web3_pk.eth.estimate_gas(tx)
        self.log.info('Gas estimate for fund native is %d', tx['gas'])
        network.tx(self, web3_pk, tx, account_pk, persist_nonce=persist_nonce, txstr='value transfer')

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
        elif self.env == 'optimism.sepolia':
            return OptimismSepolia(self, name, **kwargs)
        elif self.env == 'sepolia':
            return Sepolia(self, name, **kwargs)

        return DefaultPostLondon(self, name, **kwargs)

    def get_l1_network_connection(self, name='primary_l1_connection', **kwargs):
        """Get the layer 1 network connection used by a layer 2."""
        if self.is_ten():

            cls = globals().get(Properties().l1_abstraction(self.env))
            return cls(self, name, **kwargs)
        elif self.env == 'arbitrum.sepolia':
            return ArbitrumL1Sepolia(self, name, **kwargs)
        elif self.env == 'optimism.sepolia':
            return OptimismL1Sepolia(self, name, **kwargs)
        return DefaultPostLondon(self, name, **kwargs)


class TenNetworkTest(GenericNetworkTest):
    """The test used by all Ten specific network testcases.

    Test class specific for the Ten Network. Provides utilities for funding native ETH and ERC20 tokens in the layer1 and
    layer2 of a TEN Network.
    """

    # RPC endpoints for ten-scan.
    #
    def scan_get_batch_for_transaction(self, tx_hash):
        """Get the publicly available batch for a given transaction hash. """
        data = {"jsonrpc": "2.0", "method": "scan_getBatchByTx", "params": [tx_hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_latest_rollup_header(self):
        """Returns the header of the latest rollup. """
        data = {"jsonrpc": "2.0", "method": "scan_getLatestRollupHeader", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_approx_total_transaction_count(self):
        """Get the publicly available approximate total transaction count. """
        data = {"jsonrpc": "2.0", "method": "scan_getTotalTransactionCount", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_total_transaction_count(self):
        """Get the publicly available accurate total transaction count. """
        data = {"jsonrpc": "2.0", "method": "scan_getTotalTransactionsQuery", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_total_contract_count(self):
        """Returns the total count of created contracts. """
        data = {"jsonrpc": "2.0", "method": "scan_getTotalContractCount", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_public_transaction_data(self, offset, size):
        """Get a publicly available list of transactions data based on offset and page size. """
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getPublicTransactionData", "params": [pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_block_listing(self, offset=0, size=10):
        """Returns a list of block headers (from the L1). """
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getBlockListing", "params": [pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_batch_listing(self, offset=0, size=10):
        """Returns a list of batches (from the L2). """
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getBatchListing", "params": [pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_batch(self, hash):
        """Returns the batch with the given hash. """
        data = {"jsonrpc": "2.0", "method": "scan_getBatch", "params": [hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_latest_batch(self):
        """Returns the header of the latest rollup at tip."""
        data = {"jsonrpc": "2.0", "method": "scan_getLatestBatch", "params": [], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_batch_by_height(self, height):
        """Returns the batch with the given height. """
        data = {"jsonrpc": "2.0", "method": "scan_getBatchByHeight", "params": [height], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_batch_by_seq(self, seq):
        """Returns the batch with the given sequence number. """
        data = {"jsonrpc": "2.0", "method": "scan_getBatchBySeq", "params": [seq], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_transaction(self, hash, return_error=False):
        """Returns the transaction. """
        data = {"jsonrpc": "2.0", "method": "scan_getTransaction", "params": [hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json():
            if return_error: return response.json()['error']['message']
            self.log.error(response.json()['error']['message'])
        return None

    def scan_get_rollup_listing(self, offset=0, size=10):
        """Returns a list of rollups. """
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getRollupListing", "params": [pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_rollup_by_hash(self, hash):
        """Returns the public rollup data given its hash. """
        data = {"jsonrpc": "2.0", "method": "scan_getRollupByHash", "params": [hash], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_rollup_batches(self, hash, offset=0, size=10):
        """Returns a list of public batch data within a given rollup hash. """
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getRollupBatches", "params": [hash, pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_rollup_by_seq_no(self, seq):
        """Returns the rollup for the batch with the given sequence. """
        data = {"jsonrpc": "2.0", "method": "scan_getRollupBySeqNo", "params": [seq], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def scan_get_batch_transactions(self, hash, offset=0, size=10):
        """Returns a list of public transaction data within a given batch hash. """
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getBatchTransactions", "params": [hash, pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    # @todo
    def scan_get_personal_transactions(self, address, offset=0, size=10):
        """Retrieves the receipts for the specified account. """
        pagination = {"offset": offset, "size": size}
        data = {"jsonrpc": "2.0", "method": "scan_getPersonalTransactions", "params": [address, pagination], "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def json_hex_to_obj(self, hex_str):
        """Convert a json hex string to an object. """
        if hex_str.startswith('0x'): hex_str = hex_str[2:]
        byte_str = bytes.fromhex(hex_str)
        json_str = byte_str.decode('utf-8')
        return json.loads(json_str)

    def scan_list_personal_txs(self, url, address, offset=0, size=10, return_error=False,
                               show_public=False, show_synthetic=False):
        """Get a list of transactions that are personally visible to a given user. """
        payload = {"address": address, "pagination": {"offset": offset, "size": size},
                   "showAllPublicTxs": show_public, "showSyntheticTxs": show_synthetic}
        data = {"jsonrpc": "2.0", "method": "eth_getStorageAt",
                "params": ["0x0000000000000000000000000000000000000002", json.dumps(payload), None], "id": self.MSG_ID }
        response = self.post(data, url)
        if 'result' in response.json(): return self.json_hex_to_obj(response.json()['result'])
        elif 'error' in response.json():
            if return_error: return response.json()['error']
            else: self.log.error(response.json()['error']['message'])
        return None

    def read_all_personal_txs(self, network, account, show_public, increment = 100):
        """Return all personal transactions for a user. """
        number = self.read_size_personal_txs(network, account, show_public)
        self.log.info('  Total transactions %d' % number)
        txs = []
        start = 0
        while number > 0:
            if number >= increment:
                self.log.info('  Reading offset %d size %d' % (start, increment))
                txs.extend(self.read_page_personal_txs(network, account, show_public, start, increment))
                number -= increment
                start += increment
            else:
                self.log.info('  Reading offset %d size %d' % (start, number))
                txs.extend(self.read_page_personal_txs(network, account, show_public, start, number))
                break
        return txs

    def read_size_personal_txs(self, network, account, show_public):
        """Return the personal transactions size for a user. """
        return self.scan_list_personal_txs(url=network.connection_url(), address=account.address,
                                           show_public=show_public, offset=0, size=1)['Total']

    def read_page_personal_txs(self, network, account, show_public, offset, size):
        """Return a page of personal transactions for a user. """
        return self.scan_list_personal_txs(url=network.connection_url(), address=account.address,
                                           show_public=show_public, offset=offset, size=size)['Receipts']

    # RPC endpoints for session key management
    #
    def get_session_key(self, url):
        """Get a session key. """
        data = {"jsonrpc": "2.0", "method": "sessionkeys_create", "params": [], "id": self.MSG_ID }
        response = self.post(data, url)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def activate_session_key(self, url):
        """Activate a session key. """
        data = {"jsonrpc": "2.0", "method": "sessionkeys_activate", "params": [], "id": self.MSG_ID }
        response = self.post(data, url)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    def deactivate_session_key(self, url):
        """Deactivate a session key. """
        data = {"jsonrpc": "2.0", "method": "sessionkeys_deactivate", "params": [], "id": self.MSG_ID }
        response = self.post(data, url)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    # RCP endpoints for debugging
    #
    def get_debug_event_log_relevancy(self, url, address, signature, fromBlock=0, toBlock='latest'):
        """Get the debug_LogVisibility. """
        data = {"jsonrpc": "2.0",
                "method": "debug_eventLogRelevancy",
                "params": [{
                    "fromBlock": fromBlock,
                    "toBlock": toBlock,
                    "address": address,
                    "topics": [signature]
                }],
                "id": self.MSG_ID }
        response = self.post(data, server=url)
        if 'result' in response.json(): return response.json()['result']
        elif 'error' in response.json(): self.log.error(response.json()['error']['message'])
        return None

    # Node health
    #
    def node_health(self, url, dump_to=None):
        """Get the validator health status."""
        data = {"jsonrpc": "2.0", "method": "ten_health", "id": self.MSG_ID}
        try:
            response = self.post(data, server=url)
            if 'result' in response.json():
                if dump_to is not None:
                    with open(os.path.join(self.output, dump_to), 'w') as file:
                        json.dump(response.json()['result'], file, indent=4)
                return response.json()['result']['OverallHealth']
            elif 'error' in response.json():
                self.log.warn(response.json()['error']['message'])
                return False
        except Exception as e:
            self.log.warn('Unable to get health status from the network')
        return False

    def validator_health(self, dump_to=None):
        """Get the validator health status."""
        url = 'http://%s:%s' % (Properties().validator_host(self.env), Properties().validator_port_http(self.env))
        return self.node_health(url, dump_to)

    def sequencer_health(self, dump_to=None):
        """Get the sequencer health status."""
        url = 'http://%s:%s' % (Properties().sequencer_host(self.env), Properties().sequencer_port_http(self.env))
        return self.node_health(url, dump_to)

    def wait_for_node(self, health_fn, timeout=60):
        """Wait for a node to be healthy"""
        self.log.info('Waiting for network to be healthy ...')
        start = time.time()
        count = 0
        while True:
            count=count+1
            if (time.time() - start) > timeout:
                self.addOutcome(TIMEDOUT, 'Timed out waiting %d secs for node to be healthy'%timeout, abortOnError=True)
            if health_fn(dump_to='health.%d.out'%count):
                self.log.info('Node is healthy after %d secs'%(time.time() - start))
                break
            else: self.log.info('Reported node health status is false ... waiting')
            time.sleep(3.0)

    def wait_for_validator(self, timeout=120):
        self.wait_for_node(self.validator_health, timeout)

    def wait_for_sequencer(self, timeout=120):
        self.wait_for_node(self.sequencer_health, timeout)

    # Utility methods
    #
    def ten_get_xchain_proof(self, type, xchain_message):
        """Get the xchain proof for a given message. """
        data = {"jsonrpc": "2.0",
                "method": "ten_getCrossChainProof",
                "params": [type, xchain_message],
                "id": self.MSG_ID }
        response = self.post(data)
        if 'result' in response.json():
            return response.json()['result']['Proof'], response.json()['result']['Root']
        elif 'error' in response.json():
            self.log.warn('Error getting proof, reason = %s', response.json()['error']['message'])
        return None, None

    def post(self, data, server=None):
        """Post to the node host. """
        self.MSG_ID += 1
        if not server:
            server = 'http://%s:%s' % (Properties().validator_host(self.env), Properties().validator_port_http(self.env))
        return requests.post(server, json=data)

    def ratio_failures(self, file, threshold=0.05):
        """Search through a log for failure ratios and fail if above a threshold. """
        ratio = 0
        regex = re.compile('Ratio failures = (?P<ratio>.*)$', re.M)
        with open(file, 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None:
                    ratio = float(result.group('ratio'))
        self.log.info('Ratio of failures is %.2f' % ratio)
        if ratio > threshold: self.addOutcome(FAILED, outcomeReason='Failure ratio > 0.05', abortOnError=False)
        return ratio

    def txs_sent(self, file):
        """Search through a log for number of transactions sent. """
        regex = re.compile('Number of transactions sent = (?P<sent>.*)$', re.M)
        with open(file, 'r') as fp:
            for line in fp.readlines():
                result = regex.search(line)
                if result is not None: return int(result.group('sent'))
        return 0