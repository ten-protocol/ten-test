import os, copy, sys, json, requests
from pysys.basetest import BaseTest
from pysys.constants import PROJECT, BACKGROUND
from obscuro.test.networks.obscuro import Obscuro
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.wallet_extension import WalletExtension


class GenericNetworkTest(BaseTest):
    """The base test used by all tests cases, against any request environment.

    The GenericNetworkTest class provides common utilities used by all tests, which at the moment are the ability to
    start processes outside of the framework to interact with the network, e.g. written in python or javascript. The
    WEBSOCKET and PROXY values can be set at run time using the -X<ATTRIBUTE> option to the pysys run launcher, and
    respectively force all connections to be over websockets, or for a proxy to set inbetween the client and network
    where a test supports these.

    """
    ALLOW_EVENT_DUPLICATES = True   # if true we allow duplicate event logs in the test validation
    WEBSOCKET = False               # run with `pysys.py run -XWEBSOCKET` to enable
    PROXY = False                   # run with `pysys.py run -XPROXY` to enable
    MSG_ID = 1

    def __init__(self, descriptor, outsubdir, runner):
        """Call the parent constructor but set the mode to obscuro if non is set. """
        super().__init__(descriptor, outsubdir, runner)
        self.env = 'obscuro' if self.mode is None else self.mode
        self.block_time = Properties().block_time_secs(self.env)

        # every test runs a default wallet extension
        if self.is_obscuro(): self.run_wallet(Obscuro.PORT, Obscuro.WS_PORT)

    def is_obscuro(self):
        """Return true if we are running against an Obscuro network. """
        return self.env in ['obscuro', 'obscuro.dev', 'obscuro.local', 'obscuro.sim']

    def is_obscuro_sim(self):
        """Return true if we are running against an Obscuro simulation network. """
        return self.env in ['obscuro.sim']

    def run_wallet(self, port, ws_port):
        """Run a single wallet extension for use by the tests. """
        extension = WalletExtension(self, port, ws_port, name='primary')
        return extension.run()

    def run_python(self, script, stdout, stderr, args=None, state=BACKGROUND, timeout=120):
        """Run a python process."""
        self.log.info('Running python script %s' % os.path.basename(script))
        arguments = [script]
        if args is not None: arguments.extend(args)

        environ = copy.deepcopy(os.environ)
        hprocess = self.startProcess(command=sys.executable, displayName='python', workingDir=self.output,
                                     arguments=arguments, environs=environ, stdout=stdout, stderr=stderr,
                                     state=state, timeout=timeout)
        return hprocess

    def run_javascript(self, script, stdout, stderr, args=None, state=BACKGROUND, timeout=120):
        """Run a javascript process."""
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


class ObscuroNetworkTest(GenericNetworkTest):
    """The test used by all Obscuro specific network testcases.

    Test class specific for the Obscuro Network. Provides utilities for funding OBX and ERC20 tokens in the layer1 and
    layer2 of an Obscuro Network.
    """

    def fund_eth(self, network, web3_from, account_from, web3_to, account_to, eth_amount):
        """A native transfer of ETH from one address to another."""
        from_eth = web3_from.eth.get_balance(account_from.address)
        to_eth = web3_to.eth.get_balance(account_to.address)
        self.log.info('From balance = %f ' % web3_from.fromWei(from_eth, 'ether'))
        self.log.info('To balance = %f ' % web3_to.fromWei(to_eth, 'ether'))

        tx = {
            'chainId': network.chain_id(),
            'nonce': web3_from.eth.get_transaction_count(account_from.address),
            'to': account_to.address,
            'value': web3_from.toWei(eth_amount, 'ether'),
            'gas': 4*21000,
            'gasPrice': web3_from.eth.gas_price
        }
        tx_sign = account_from.sign_transaction(tx)
        tx_hash = network.send_transaction(self, web3_from, tx_sign)
        network.wait_for_transaction(self, web3_from, tx_hash)

        from_eth = web3_from.eth.get_balance(account_from.address)
        to_eth = web3_to.eth.get_balance(account_to.address)
        self.log.info('From balance = %f ' % web3_from.fromWei(from_eth, 'ether'))
        self.log.info('To balance = %f ' % web3_to.fromWei(to_eth, 'ether'))

    def fund_obx(self, network, account, amount, web3=None):
        """Fund OBX in the L2 to a users account, either through the faucet server or direct from the account."""
        if self.env in ['obscuro', 'obscuro.dev']:
            self.fund_obx_from_faucet_server(account, web3)
        else:
            self.fund_obx_from_funded_pk(network, account, amount, web3)

    def fund_obx_from_faucet_server(self, account, web3=None):
        """Allocates native OBX to a users account from the faucet server."""
        if web3 is not None:
            user_obx = web3.eth.get_balance(account.address)
            self.log.info('OBX User balance   = %d ' % user_obx)

        self.log.info('Running request on %s' % Properties().faucet_url(self.env))
        self.log.info('Running for user address %s' % account.address)
        headers = {'Content-Type': 'application/json'}
        data = {"address": account.address}
        requests.post(Properties().faucet_url(self.env), data=json.dumps(data), headers=headers)

        if web3 is not None:
            user_obx = web3.eth.get_balance(account.address)
            self.log.info('OBX User balance   = %d ' % user_obx)

    def fund_obx_from_funded_pk(self, network, account, amount, web3=None):
        """Allocates native OBX to a users account from the pre-funded account."""
        if web3 is not None:
            user_obx = web3.eth.get_balance(account.address)
            self.log.info('OBX User balance   = %d ' % user_obx)
            if user_obx < amount: amount = amount - user_obx

        web3_funded, account_funded = network.connect(self, Properties().l2_funded_account_pk(self.env))
        tx = {
            'nonce': web3_funded.eth.get_transaction_count(account_funded.address),
            'to': account.address,
            'value': amount,
            'gas': 4 * 720000,
            'gasPrice': 21000
        }
        tx_sign = account_funded.sign_transaction(tx)
        tx_hash = network.send_transaction(self, web3_funded, tx_sign)
        network.wait_for_transaction(self, web3_funded, tx_hash)

        if web3 is not None:
            user_obx = web3.eth.get_balance(account.address)
            self.log.info('OBX User balance   = %d ' % user_obx)

    def transfer_token(self, network, token_name, token_address, web3_from, account_from, address, amount):
        """Transfer an ERC20 token amount from a recipient account to an address. """
        self.log.info('Running for token %s' % token_name)

        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3_from.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account_from.address).call()
        self.log.info('%s User balance   = %d ' % (token_name, balance))
        network.transact(self, web3_from, token.functions.transfer(address, amount), account_from, 7200000)

        balance = token.functions.balanceOf(account_from.address).call()
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

    def get_total_transactions(self):
        """Return the total number of L2 transactions on Obscuro."""
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
        server = 'http://%s:%s' % (Properties().node_host(self.env), Properties().node_port_http(self.env))
        return requests.post(server, json=data)
