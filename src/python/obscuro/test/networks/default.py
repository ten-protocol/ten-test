from web3 import Web3
from web3.exceptions import TimeExhausted
from pysys.constants import *
from obscuro.test.utils.properties import Properties


class Default:
    """A default connection giving access to an underlying network."""
    ETH_LIMIT = 0.0001
    ETH_ALLOC = 0.0002
    GAS_MULT = 2
    CURRENCY = 'ETH'

    def __init__(self, test, name=None, **kwargs):
        props = Properties()
        self.test = test
        self.name = name
        self.log = test.log
        self.verbose = kwargs['verbose'] if 'verbose' in kwargs else False
        self.HOST = props.host_http('default')
        self.WS_HOST = props.host_ws('default')
        self.PORT = props.port_http('default')
        self.WS_PORT = props.port_ws('default')
        self.CHAIN_ID = props.chain_id('default')

    def chain_id(self): return self.CHAIN_ID

    def connection_url(self, web_socket=False):
        """Return the connection URL to the network. """
        port = self.PORT if not web_socket else self.WS_PORT
        host = self.HOST if not web_socket else self.WS_HOST
        return '%s:%d' % (host, port)

    def connect(self, test, private_key, web_socket=False, check_funds=True):
        """Connect to the network using a given private key. """
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.privateKeyToAccount(private_key)
        if self.verbose: test.log.info('Account %s connected to %s', account.address, self.__class__.__name__)

        if check_funds:
            balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
            if balance < self.ETH_LIMIT:
                if self.verbose: test.log.info('Account balance %.6f ETH below threshold %s', balance, self.ETH_LIMIT)
                test.distribute_native(account, self.ETH_ALLOC)
            if self.verbose: test.log.info('Account balance %.6f ETH', web3.fromWei(web3.eth.get_balance(account.address), 'ether'))
        return web3, account

    def connect_account1(self, test, web_socket=False, check_funds=True):
        """Connect account 1 to the network. """
        return self.connect(test, Properties().account1pk(), web_socket, check_funds)

    def connect_account2(self, test, web_socket=False, check_funds=True):
        """Connect account 2 to the network. """
        return self.connect(test, Properties().account2pk(), web_socket, check_funds)

    def connect_account3(self, test, web_socket=False, check_funds=True):
        """Connect account 3 to the network. """
        return self.connect(test, Properties().account3pk(), web_socket, check_funds)

    def connect_account4(self, test, web_socket=False, check_funds=True):
        """Connect account 4 to the network. """
        return self.connect(test, Properties().account4pk(), web_socket, check_funds)

    def tx(self, test, web3, tx, account, persist_nonce=True):
        """Transact using the supplied transaction dictionary.

        Note that the nonce and chainId will automatically be added into the transaction dictionary in this method
        and therefore do not need to be supplied by the caller.
        """
        nonce = self.get_next_nonce(test, web3, account, persist_nonce)
        tx['nonce'] = nonce
        tx['chainId'] = web3.eth.chain_id
        tx_sign = self.sign_transaction(test, tx, nonce, account, persist_nonce)
        tx_hash = self.send_transaction(test, web3, nonce, account, tx_sign, persist_nonce)
        tx_recp = self.wait_for_transaction(test, web3, nonce, account, tx_hash, persist_nonce)
        return tx_recp

    def transact(self, test, web3, target, account, gas_limit, persist_nonce=True, timeout=60):
        """Transact using either a contract constructor or contract function as the target.

        This method expects the target to be a contract constructor or function, and will build this into the
        transaction dictionary using buildTransaction on the target. The nonce will be automatically added during this
        process.
        """
        nonce = self.get_next_nonce(test, web3, account, persist_nonce)
        tx = self.build_transaction(test, web3, target, nonce, gas_limit)
        tx_sign = self.sign_transaction(test, tx, nonce, account, persist_nonce)
        tx_hash = self.send_transaction(test, web3, nonce, account, tx_sign, persist_nonce)
        tx_recp = self.wait_for_transaction(test, web3, nonce, account, tx_hash, persist_nonce, timeout=timeout)
        return tx_recp

    def get_next_nonce(self, test, web3, account, persist_nonce):
        """Get the next nonce, either from persistence or from the transaction count. """
        nonce = test.nonce_db.get_next_nonce(test, web3, account.address, test.env, persist_nonce, self.verbose)
        return nonce

    def build_transaction(self, test, web3, target, nonce, gas_limit):
        """Build the transaction dictionary from the contract constructor or function target. """

        try:
            gas_estimate = target.estimate_gas()
            if self.verbose: test.log.info('Gas estimate, cost is %d WEI', gas_estimate)
            if self.verbose: test.log.info('Total potential cost is %d WEI', gas_estimate*web3.eth.gas_price)
            gas_estimate = gas_estimate * self.GAS_MULT
        except Exception as e:
            test.log.warn('Gas estimate, %s' % e.args[0])
            gas_estimate = gas_limit

        build_tx = target.buildTransaction(
            {
                'nonce': nonce,
                'chainId': web3.eth.chain_id,
                'gasPrice': web3.eth.gas_price,   # the price we are willing to pay per gas unit (dimension is gwei)
                'gas': gas_estimate               # max gas units prepared to pay (dimension is computational units)
            }
        )
        return build_tx

    def sign_transaction(self, test, tx, nonce, account, persist_nonce):
        """Sign a transaction. """
        signed_tx = account.sign_transaction(tx)
        if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'SIGNED')
        return signed_tx

    def send_transaction(self, test, web3, nonce, account, signed_tx, persist_nonce):
        """Send the signed transaction to the network. """
        tx_hash = None
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'SENT')
        except Exception as e:
            test.log.error('Error sending raw transaction %s', e)
            test.log.warn('Deleting nonce entries in the persistence for nonce %d', nonce)
            if persist_nonce: test.nonce_db.delete_entries(account.address, test.env, nonce)
            test.addOutcome(BLOCKED, abortOnError=True)
        if self.verbose: test.log.info('Transaction sent with hash %s', tx_hash.hex())
        return tx_hash

    def wait_for_transaction(self, test, web3, nonce, account, tx_hash, persist_nonce, timeout=30):
        """Wait for the transaction from the network to be acknowledged. """
        tx_receipt = None
        try:
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)

            if tx_receipt.status == 1:
                if self.verbose: test.log.info('Transaction receipt block hash %s', tx_receipt.blockHash.hex())
                if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'CONFIRMED')
            else:
                if self.verbose: test.log.error('Transaction receipt failed')
                if self.verbose: test.log.error('Full receipt: %s', tx_receipt)
                if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'FAILED')
                test.addOutcome(FAILED, abortOnError=True)

        except TimeExhausted as e:
            test.log.error('Transaction timed out %s', e)
            test.log.warn('Deleting nonce entries in the persistence for nonce %d', nonce)
            if persist_nonce: test.nonce_db.delete_entries(account.address, test.env, nonce)
            test.addOutcome(TIMEDOUT, abortOnError=True)

        return tx_receipt
