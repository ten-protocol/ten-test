import time, json
from web3 import Web3
from web3.datastructures import AttributeDict
from web3.exceptions import TimeExhausted
from pysys.constants import *
from ten.test.utils.properties import Properties


def attributedict_to_dict(obj):
    """Convert a web3.datastructures.AttributeDict to a regular dictionary."""
    if isinstance(obj, AttributeDict):
        data = {}
        for (key, value) in obj.items():
            data[key] = attributedict_to_dict(value)
        return data
    elif isinstance(obj, list):
        return [attributedict_to_dict(item) for item in obj]
    elif isinstance(obj, bytes):
        return obj.hex()
    else:
        return obj


class DefaultPostLondon:
    """A default connection giving access to an underlying network.

    Note that the default assumes post London fork with the EIP-1599 fee market change."""
    ETH_LIMIT = 0.001                   # lower than this then allocate more funds
    ETH_ALLOC = 0.005                   # the allocation amount (for configured accounts)
    ETH_ALLOC_EPHEMERAL = 0.001         # the allocation amount (for ephemeral accounts)

    def __init__(self, test, name=None, **kwargs):
        """Construct and instance of the network connection abstraction."""
        props = Properties()
        self.test = test
        self.name = name
        self.log = test.log
        self.HOST = props.host_http('default')
        self.WS_HOST = props.host_ws('default')
        self.PORT = props.port_http('default')
        self.WS_PORT = props.port_ws('default')
        self.CHAIN_ID = props.chain_id('default')

    def chain_id(self):
        """Return the network chain id."""
        return self.CHAIN_ID

    def connection_url(self, web_socket=False):
        """Return the connection URL to the network."""
        port = self.PORT if not web_socket else self.WS_PORT
        host = self.HOST if not web_socket else self.WS_HOST
        return '%s:%d' % (host, port)

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        """Connect to the network using a given private key."""
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.from_key(private_key)
        balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
        if verbose: self.log.info('Account %s connected to %s (%.6f ETH), wss=%s', account.address, self.__class__.__name__, balance, web_socket)

        if check_funds and balance < self.ETH_LIMIT:
            if verbose: self.log.info('Account %s balance is below threshold %s ... need to distribute funds', account.address, self.ETH_LIMIT)
            test.distribute_native(account, self.ETH_ALLOC)
            if verbose:
                balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
                self.log.info('Account %s balance is now %.6f ETH', account.address, balance)
        return web3, account

    def connect_account1(self, test, web_socket=False, check_funds=True, verbose=True):
        """Connect account 1 to the network."""
        return self.connect(test, Properties().account1pk(), web_socket, check_funds, verbose)

    def connect_account2(self, test, web_socket=False, check_funds=True, verbose=True):
        """Connect account 2 to the network."""
        return self.connect(test, Properties().account2pk(), web_socket, check_funds, verbose)

    def connect_account3(self, test, web_socket=False, check_funds=True, verbose=True):
        """Connect account 3 to the network."""
        return self.connect(test, Properties().account3pk(), web_socket, check_funds, verbose)

    def connect_account4(self, test, web_socket=False, check_funds=True, verbose=True):
        """Connect account 4 to the network."""
        return self.connect(test, Properties().account4pk(), web_socket, check_funds, verbose)

    def tx(self, test, web3, tx, account, persist_nonce=True, verbose=True, timeout=30):
        """Transact using the supplied transaction dictionary.

        Note that the nonce and chainId will automatically be added into the transaction dictionary in this method
        and therefore do not need to be supplied by the caller. If they are supplied, they will be overwritten.
        """
        if verbose: self.log.info('Account %s performing transaction', account.address)
        nonce = self.get_next_nonce(test, web3, account, persist_nonce, verbose)
        tx['nonce'] = nonce
        tx['chainId'] = web3.eth.chain_id
        tx_sign = self.sign_transaction(test, tx, nonce, account, persist_nonce)
        tx_hash = self.send_transaction(test, web3, nonce, account, tx_sign, persist_nonce, verbose)
        tx_recp = self.wait_for_transaction(test, web3, nonce, account, tx_hash, persist_nonce, verbose, timeout)
        if tx_recp.status != 1:
            self.replay_transaction(web3, tx, tx_recp)
            test.addOutcome(FAILED, abortOnError=True)
        return tx_recp

    def transact(self, test, web3, target, account, gas_limit, persist_nonce=True, verbose=True, timeout=30, **kwargs):
        """Transact using either a contract constructor or contract function as the target.

        This method expects the target to be a contract constructor or function, and will build this into the
        transaction dictionary using build_transaction on the target. The nonce will automatically be added during this
        process.
        """
        self.log.info('Account %s performing transaction', account.address)
        nonce = self.get_next_nonce(test, web3, account, persist_nonce, verbose)
        tx = self.build_transaction(test, web3, target, nonce, account, gas_limit, verbose, **kwargs)
        tx_sign = self.sign_transaction(test, tx, nonce, account, persist_nonce)
        tx_hash = self.send_transaction(test, web3, nonce, account, tx_sign, persist_nonce, verbose)
        tx_recp = self.wait_for_transaction(test, web3, nonce, account, tx_hash, persist_nonce, verbose, timeout)
        if tx_recp.status != 1:
            self.replay_transaction(web3, tx, tx_recp)
            test.addOutcome(FAILED, abortOnError=True)
        return tx_recp

    def get_next_nonce(self, test, web3, account, persist_nonce, verbose=True):
        """Get the next nonce, either from persistence or from the transaction count."""
        nonce = test.nonce_db.get_next_nonce(test, web3, account.address, test.env, persist_nonce, verbose)
        return nonce

    def build_transaction(self, test, web3, target, nonce, account, gas_limit, verbose=True, **kwargs):
        """Build the transaction dictionary from the contract constructor or function target."""
        estimate = kwargs['estimate'] if 'estimate' in kwargs else True
        gas_attempts = int(kwargs['gas_attempts']) if 'gas_attempts' in kwargs else 1
        base_fee_per_gas = web3.eth.get_block('latest').baseFeePerGas
        max_priority_fee_per_gas = web3.to_wei(1, 'gwei')
        max_fee_per_gas = (5 * base_fee_per_gas) + max_priority_fee_per_gas
        balance = web3.eth.get_balance(account.address)

        gas_estimate = gas_limit
        params = {
            'from': account.address,                          # the account originating the transaction
            'nonce': nonce,                                   # the nonce to use
            'chainId': web3.eth.chain_id,                     # the chain id
            'maxFeePerGas': max_fee_per_gas,                  # Maximum amount you’re willing to pay
            'maxPriorityFeePerGas': max_priority_fee_per_gas  # Priority fee to include the transaction in the block
        }
        if 'access_list' in kwargs: params['accessList'] = kwargs['access_list']
        if estimate:
            while gas_attempts > 0:
                try:
                    gas_estimate = target.estimate_gas(params)
                    break
                except Exception as e:
                    self.log.warn('Error estimating gas needed, %s' % e.args[0])
                    gas_attempts -= 1
                    time.sleep(5)

        if verbose:
            self.log.info('Gas %d, base fee %d WEI, cost %d WEI, balance %.18f ETH',
                          gas_estimate, base_fee_per_gas, web3.from_wei(base_fee_per_gas*gas_estimate, 'wei'),
                          web3.from_wei(balance, 'ether'))

        params['gas'] = int(1.1*gas_estimate)
        build_tx = target.build_transaction(params)
        return build_tx

    def sign_transaction(self, test, tx, nonce, account, persist_nonce):
        """Sign a transaction."""
        signed_tx = account.sign_transaction(tx)
        if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'SIGNED')
        return signed_tx

    def send_transaction(self, test, web3, nonce, account, signed_tx, persist_nonce, verbose=True):
        """Send the signed transaction to the network."""
        tx_hash = None
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'SENT')
        except Exception as e:
            self.log.error('Error sending raw transaction %s', e)
            if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'TIMEDOUT')
            test.addOutcome(BLOCKED, abortOnError=True)
        if verbose: self.log.info('Transaction sent with hash %s', tx_hash.hex())
        return tx_hash

    def wait_for_transaction(self, test, web3, nonce, account, tx_hash, persist_nonce, verbose=True, timeout=30):
        """Wait for the transaction from the network to be acknowledged."""
        tx_receipt = None
        try:
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)

            if tx_receipt.status == 1:
                if verbose: self.log.info('Transaction receipt block hash %s', tx_receipt.blockHash.hex())
                if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'CONFIRMED')
            else:
                self.log.error('Transaction receipt failed')
                self.log.error('Full receipt: %s', tx_receipt)
                if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'FAILED')

        except TimeExhausted as e:
            self.log.error('Transaction timed out %s', e)
            if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'TIMEDOUT')
            test.addOutcome(TIMEDOUT, abortOnError=True)

        return tx_receipt

    def replay_transaction(self, web3, tx, tx_recp):
        """Replay a transaction to get a failure reason."""
        try:
            web3.eth.call(tx, block_identifier=tx_recp.blockNumber)
            self.log.warn('Replaying the transaction did not throw an error')
        except Exception as e:
            self.log.error('Replay call: %s', e)

    def dump(self, obj, filename):
        """Dump a web3 transaction response to output file. """
        tx_dict = attributedict_to_dict(obj)
        with open(os.path.join(self.test.output, filename), 'w') as file:
            json.dump(tx_dict, file, indent=4)


class DefaultPreLondon(DefaultPostLondon):
    """Default connection pre the london fork."""

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)

    def build_transaction(self, test, web3, target, nonce, account, gas_limit, verbose=True, **kwargs):
        """Build the transaction dictionary from the contract constructor or function target. """
        estimate = kwargs['estimate'] if 'estimate' in kwargs else True
        gas_attempts = int(kwargs['gas_attempts']) if 'gas_attempts' in kwargs else 1
        balance = web3.eth.get_balance(account.address)

        gas_estimate = gas_limit
        gas_price = web3.eth.gas_price
        params = {
            'from': account.address,          # the account originating the transaction
            'nonce': nonce,                   # the nonce to use
            'chainId': web3.eth.chain_id,     # the chain id
            'gasPrice': gas_price             # the current gas price
        }
        if 'access_list' in kwargs: params['accessList'] = kwargs['access_list']
        if estimate:
            while gas_attempts > 0:
                try:
                    gas_estimate = target.estimate_gas(params)
                    break
                except Exception as e:
                    self.log.warn('Error estimating gas needed, %s' % e.args[0])
                    gas_attempts -= 1
                    time.sleep(5)

        if verbose:
            self.log.info('Gas %d, price %d WEI, cost %d WEI, balance %.18F ETH',
                          gas_estimate, gas_price, web3.from_wei(gas_price*gas_estimate, 'wei'),
                          web3.from_wei(balance, 'ether'))

        params['gas'] = int(1.1*gas_estimate)
        build_tx = target.build_transaction(params)
        return build_tx