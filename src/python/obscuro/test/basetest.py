import os, copy, sys, json, requests, secrets
from web3 import Web3
from pysys.basetest import BaseTest
from pysys.constants import PROJECT, BACKGROUND
from obscuro.test.persistence.nonce import NoncePersistence
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.wallet_extension import WalletExtension


class GenericNetworkTest(BaseTest):
    """The base test used by all tests cases, against any request environment.

    The GenericNetworkTest class provides common utilities used by all tests, which at the moment are the ability to
    start processes outside of the framework to interact with the network, e.g. written in python or javascript. The
    WEBSOCKET and PROXY values can be set at run time using the -X<ATTRIBUTE> option to the pysys run launcher, and
    respectively force all connections to be over websockets, or for a proxy to sit inbetween the client and network
    (where a test supports these). To override the node host FQDN (e.g. to target a specific node, rather than go
    through a

    """
    WEBSOCKET = False               # if true use websockets for all comms to the wallet extension
    PROXY = False                   # if true run all websocket connections through a recording proxy
    MSG_ID = 1                      # global used for http message requests numbers
    NODE_HOST = None                # if not none overrides the node host from the properties file

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to obscuro if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.env = 'obscuro' if self.mode is None else self.mode
        self.block_time = Properties().block_time_secs(self.env)

        # every test has its own connection to the nonce db
        self.nonce_db = NoncePersistence(runner.obscuro_runner.db_dir)
        self.addCleanupFunction(self.close_db)

        # every test runs a default wallet extension
        if self.is_obscuro(): self.wallet_extension = self.run_wallet()

    def close_db(self):
        """Close the connection to the nonce database on completion. """
        self.nonce_db.close()

    def is_obscuro(self):
        """Return true if we are running against an Obscuro network. """
        return self.env in ['obscuro', 'obscuro.dev', 'obscuro.local', 'obscuro.sim']

    def is_obscuro_sim(self):
        """Return true if we are running against an Obscuro simulation network. """
        return self.env in ['obscuro.sim']

    def run_wallet(self, port=None, ws_port=None):
        """Run a single wallet extension for use by the tests. """
        extension = WalletExtension(self, port, ws_port, name='primary')
        extension.run()
        return extension

    def run_python(self, script, stdout, stderr, args=None, state=BACKGROUND, timeout=120):
        """Run a python process. """
        self.log.info('Running python script %s' % os.path.basename(script))
        arguments = [script]
        if args is not None: arguments.extend(args)

        environ = copy.deepcopy(os.environ)
        hprocess = self.startProcess(command=sys.executable, displayName='python', workingDir=self.output,
                                     arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                                     state=state, timeout=timeout)
        return hprocess

    def run_javascript(self, script, stdout, stderr, args=None, state=BACKGROUND, timeout=120):
        """Run a javascript process. """
        self.log.info('Running javascript %s' % os.path.basename(script))
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

    def fund_eth(self, network, account, amount, pk):
        """A native transfer of ETH from one address to another. """
        web3_l1, account_l1 = network.connect(self, pk)
        nonce = network.get_next_nonce(self, web3_l1, account_l1, False)
        tx = {
            'chainId': network.chain_id(),
            'nonce': nonce,
            'to': account.address,
            'value': web3_l1.toWei(amount, 'ether'),
            'gas': 4*21000,
            'gasPrice': web3_l1.eth.gas_price
        }
        tx_sign = account_l1.sign_transaction(tx)
        tx_hash = network.send_transaction(self, web3_l1, nonce, account_l1, tx_sign, False)
        network.wait_for_transaction(self, web3_l1, nonce, account_l1, tx_hash, False)

    def fund_obx(self, network, account, amount):
        """Fund OBX in the L2 to a users account, either through the faucet server or direct from the account. """
        if self.env in ['obscuro', 'obscuro.dev']:
            self.fund_obx_from_faucet_server(account)
        else:
            self.fund_obx_from_funded_pk(network, account, amount)

    def fund_obx_from_faucet_server(self, account):
        """Allocates native OBX to a users account from the faucet server. """
        self.log.info('Running request on %s' % Properties().faucet_url(self.env))
        self.log.info('Running for user address %s' % account.address)
        headers = {'Content-Type': 'application/json'}
        data = {"address": account.address}
        requests.post(Properties().faucet_url(self.env), data=json.dumps(data), headers=headers)

    def fund_obx_from_funded_pk(self, network, account, amount):
        """Allocates native OBX to a users account from the pre-funded account.

        Note that as the L2 pre-funded account is not in our control we do not use local persistence for the nonce.
        A better approach is to always use the faucet server even on local testnet deployments.
        """
        web3_funded, account_funded = network.connect(self, Properties().l2_funded_account_pk(self.env), check_funds=False)
        nonce = network.get_next_nonce(self, web3_funded, account_funded, False)
        tx = {
            'nonce': nonce,
            'to': account.address,
            'value': web3_funded.toWei(amount, 'ether'),
            'gas': 4 * 720000,
            'gasPrice': 21000
        }
        tx_sign = account_funded.sign_transaction(tx)
        tx_hash = network.send_transaction(self, web3_funded, nonce, account_funded, tx_sign, False)
        network.wait_for_transaction(self, web3_funded, nonce, account_funded, tx_hash, False)

    def transfer_token(self, network, token_name, token_address, web3_from, account_from, address,
                       amount, persist_nonce=True):
        """Transfer an ERC20 token amount from a recipient account to an address. """
        self.log.info('Running for token %s' % token_name)

        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3_from.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account_from.address).call({"from":account_from.address})
        self.log.info('%s User balance   = %d ' % (token_name, balance))
        network.transact(self, web3_from, token.functions.transfer(address, amount), account_from, 7200000, persist_nonce)

        balance = token.functions.balanceOf(account_from.address).call({"from":account_from.address})
        self.log.info('%s User balance   = %d ' % (token_name, balance))

    def print_token_balance(self, token_name, token_address, web3, account):
        """Print an ERC20 token balance of a recipient account. """
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account.address).call()
        self.log.info('%s User balance   = %d ' % (token_name, balance))

    def get_token_balance(self, token_address, web3, account):
        """Get the ERC20 token balance of a recipient account. """
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3.eth.contract(address=token_address, abi=json.load(f))
        return token.functions.balanceOf(account.address).call()


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

    def post(self, data):
        self.MSG_ID += 1
        server = 'http://%s:%s' % (Properties().node_host(self), Properties().node_port_http(self.env))
        return requests.post(server, json=data)

    def background_funders(self, network, num_funders):
        funders = [secrets.token_hex() for _ in range(0, num_funders)]

        for i in range(0, len(funders)):
            recipients = [Web3().eth.account.privateKeyToAccount(x).address for x in funders if x != funders[i]]
            self.funds_client(network, funders[i], recipients, i)

    def funds_client(self, network, pk, recipients, num):
        wallet = WalletExtension.start(self, name='funds_%d' % num)
        self.fund_obx(network, Web3().eth.account.privateKeyToAccount(pk), 10)

        stdout = os.path.join(self.output, 'funds_%d.out' % num)
        stderr = os.path.join(self.output, 'funds_%d.err' % num)
        script = os.path.join(PROJECT.root, 'src', 'python', 'scripts', 'funds_client.py')
        args = []
        args.extend(['--network_http', '%s' % wallet.connection_url()])
        args.extend(['--pk_to_register', '%s' % pk])
        args.extend(['--recipients', ','.join([str(i) for i in recipients])])
        self.run_python(script, stdout, stderr, args)
        self.waitForGrep(file=stdout, expr='Client running', timeout=10)