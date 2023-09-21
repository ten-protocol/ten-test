import os, copy, sys, json
import threading, requests, secrets
from web3 import Web3
from pathlib import Path
from pysys.basetest import BaseTest
from pysys.constants import PROJECT, BACKGROUND
from obscuro.test.persistence.nonce import NoncePersistence
from obscuro.test.persistence.contract import ContractPersistence
from obscuro.test.utils.properties import Properties
from obscuro.test.networks.default import Default
from obscuro.test.networks.ganache import Ganache
from obscuro.test.networks.goerli import Goerli
from obscuro.test.networks.arbitrum import Arbitrum
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.networks.obscuro import ObscuroL1


class GenericNetworkTest(BaseTest):
    """The base test used by all tests cases, against any request environment. """
    MSG_ID = 1                      # global used for http message requests numbers
    NODE_HOST = None                # if not none overrides the node host from the properties file

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to obscuro if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.log.info('Running test in thread %s', threading.currentThread().getName())
        print("test1")
        self.env = 'obscuro' if self.mode is None else self.mode
        print("test2")
        self.block_time = Properties().block_time_secs(self.env)
        print("test3")

        # every test has its own connection to the nonce and contract db
        db_dir = os.path.join(str(Path.home()), '.obscurotest')
        print("test4")
        self.nonce_db = NoncePersistence(db_dir)
        print("test5")
        self.contract_db = ContractPersistence(db_dir)
        print("test6")
        self.addCleanupFunction(self.close_db)
        print("test7")
        # every test has a connection for the funded account
        self.network_funding = self.get_network_connection(name='funding_connection')
        print("test8")

    def close_db(self):
        """Close the connection to the nonce database on completion. """
        self.nonce_db.close()
        self.contract_db.close()

    def is_obscuro(self):
        """Return true if we are running against an Obscuro network. """
        return self.env in ['obscuro', 'obscuro.dev', 'obscuro.local']

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
        self.network_funding.tx(self, web3_pk, tx, account_pk)

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
            return Obscuro(self, name, **kwargs)
        elif self.env == 'goerli':
            return Goerli(self, name, **kwargs)
        elif self.env == 'ganache':
            return Ganache(self, name, **kwargs)
        elif self.env == 'arbitrum':
            return Arbitrum(self, name, **kwargs)
        return Default(self, name, **kwargs)

    def get_l1_network_connection(self, name='primary_l1_connection'):
        """Get the layer 1 network connection used by a layer 2."""
        if self.is_obscuro():
            return ObscuroL1(self, name)
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
        self.log.info(server)
        return requests.post(server, json=data)

    def background_funders(self, network, num_funders):
        funders = [secrets.token_hex() for _ in range(0, num_funders)]

        for i in range(0, len(funders)):
            recipients = [Web3().eth.account.privateKeyToAccount(x).address for x in funders if x != funders[i]]
            self.funds_client(network, funders[i], recipients, i)

    def funds_client(self, pk, recipients, num):
        network = self.get_network_connection(name='funds_%d' % num)
        network.connect(self, private_key=pk)
        self.distribute_native(Web3().eth.account.privateKeyToAccount(pk), 1)

        stdout = os.path.join(self.output, 'funds_%d.out' % num)
        stderr = os.path.join(self.output, 'funds_%d.err' % num)
        script = os.path.join(PROJECT.root, 'src', 'python', 'scripts', 'funds_client.py')
        args = []
        args.extend(['--network_http', '%s' % network.connection_url()])
        args.extend(['--pk_to_register', '%s' % pk])
        args.extend(['--recipients', ','.join([str(i) for i in recipients])])
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Client running', timeout=10)