import os, copy, sys, json, requests
from pysys.basetest import BaseTest
from pysys.constants import PROJECT, BACKGROUND
from obscuro.test.utils.properties import Properties
from obscuro.test.helpers.wallet_extension import WalletExtension
from obscuro.test.networks.obscuro import Obscuro


class ObscuroTest(BaseTest):
    """The base test used by all tests cases, against any request environment.

    The ObscuroTest class provides common utilities used by all tests, which at the moment are the ability to
    start processes outside of the framework to interact with the network, e.g. written in python or javascript. The
    WEBSOCKET and PROXY values can be set at run time using the -X<ATTRIBUTE> option to the pysys run launcher, and
    respectively force all connections to be over websockets, or for a proxy to set inbetween the client and network
    where a test supports these.

    """
    WEBSOCKET = False   # run with `pysys.py run -XWEBSOCKET` to enable
    PROXY = False       # run with `pysys.py run -XPROXY` to enable
    ONE_GIGA = 1000000000000000000

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

    def fund_eth(self, network, web3_from, account_from, web3_to, account_to, eth_amount):
        """A native transfer of ETH from one address to another."""
        from_eth = web3_from.eth.get_balance(account_from.address)
        to_eth = web3_to.eth.get_balance(account_to.address)
        self.log.info('ETH balance before;')
        self.log.info('  From balance = %f ' % web3_from.fromWei(from_eth, 'ether'))
        self.log.info('  To balance = %f ' % web3_to.fromWei(to_eth, 'ether'))

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
        self.log.info('ETH balance after;')
        self.log.info('  From balance = %f ' % web3_from.fromWei(from_eth, 'ether'))
        self.log.info('  To balance = %f ' % web3_to.fromWei(to_eth, 'ether'))

    def fund_obx(self, network, web3, account, amount):
        """Fund OBX in the L2 to a users account, either through the faucet server or direct from the account."""
        if self.env in ['obscuro', 'obscuro.dev']:
            self.__obx_from_faucet_server(web3, account)
        else:
            self.__obx_from_funded_pk(network, web3, account, amount)

    def transfer_token(self, network, token_name, token_address, web3_from, account_from, address, amount):
        """Transfer an ERC20 token amount from a recipient account to an address. """
        self.log.info('Running for token %s' % token_name)

        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3_from.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account_from.address).call()
        self.log.info('Sender token balance before = %d ' % balance)

        # transfer tokens from the funded account to the distro account
        network.transact(self, web3_from, token.functions.transfer(address, amount), account_from, 7200000)

        balance = token.functions.balanceOf(account_from.address).call()
        self.log.info('Sender token balance after = %d ' % balance)

    def print_token_balance(self, token_name, token_address, web3, account):
        """Print an ERC20 token balance of a recipient account. """
        with open(os.path.join(PROJECT.root, 'src', 'solidity', 'contracts', 'erc20', 'erc20.json')) as f:
            token = web3.eth.contract(address=token_address, abi=json.load(f))

        balance = token.functions.balanceOf(account.address).call()
        self.log.info('Token balance for %s = %d ' % (token_name, balance))

    def __obx_from_faucet_server(self, web3, account):
        """Allocates native OBX to a users account from the faucet server."""
        self.log.info('Running for native OBX token using faucet server')
        user_obx = web3.eth.get_balance(account.address)
        self.log.info('L2 balances before;')
        self.log.info('  OBX User balance   = %d ' % user_obx)

        self.log.info('Running request on %s' % Properties().faucet_url(self.env))
        self.log.info('Running for user address %s' % account.address)
        headers = {'Content-Type': 'application/json'}
        data = {"address": account.address}
        requests.post(Properties().faucet_url(self.env), data=json.dumps(data), headers=headers)

        user_obx = web3.eth.get_balance(account.address)
        self.log.info('L2 balances after;')
        self.log.info('  OBX User balance   = %d ' % user_obx)

    def __obx_from_funded_pk(self, network, web3, account, amount):
        """Allocates native OBX to a users account from the pre-funded account."""
        self.log.info('Running for native OBX token using faucet pk')

        web3_funded, account_funded = network.connect(self, Properties().l2_funded_account_pk(self.env))
        funded_obx = web3_funded.eth.get_balance(account_funded.address)
        user_obx = web3.eth.get_balance(account.address)
        self.log.info('L2 balances before;')
        self.log.info('  OBX Funded balance = %d ' % funded_obx)
        self.log.info('  OBX User balance   = %d ' % user_obx)

        if user_obx < amount:
            amount = amount - user_obx

            # transaction from the faucet to the deployment account
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

            funded_obx = web3_funded.eth.get_balance(account_funded.address)
            user_obx = web3.eth.get_balance(account.address)
            self.log.info('L2 balances after;')
            self.log.info('  OBX Funded balance = %d ' % funded_obx)
            self.log.info('  OBX User balance   = %d ' % user_obx)


