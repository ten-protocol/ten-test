from pysys.constants import FAILED
from ten.test.utils.properties import Properties
from ten.test.networks.default import DefaultPostLondon


class Sepolia(DefaultPostLondon):
    """A Sepolia connection giving access to the underlying network."""
    ETH_LIMIT = 0.1
    ETH_ALLOC = 0.5

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.host_http('sepolia')
        self.WS_HOST = props.host_ws('sepolia')
        self.PORT = props.port_http('sepolia')
        self.WS_PORT = props.port_ws('sepolia')
        self.CHAIN_ID = props.chain_id('sepolia')

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().sepoliaAPIKey())

    def transact_unsigned(self, test, web3, target, account, gas_limit, persist_nonce=True, verbose=True, timeout=30, **kwargs):
        """Transact unsigned using either a contract constructor or contract function as the target.

        This method expects the target to be a contract constructor or function, and will build this into the
        transaction dictionary using build_transaction on the target. The nonce will automatically be added during this
        process.
        """
        self.log.info('Account %s performing transaction', account.address)
        nonce = self.get_next_nonce(test, web3, account, persist_nonce, verbose)
        tx = self.build_transaction(test, web3, target, nonce, account, gas_limit, verbose, **kwargs)
        tx_hash = self.send_unsigned_transaction(test, web3, nonce, account, tx, persist_nonce, verbose)
        tx_recp = self.wait_for_transaction(test, web3, nonce, account, tx_hash, persist_nonce, verbose, timeout)
        if tx_recp.status != 1:
            self.replay_transaction(web3, tx, tx_recp)
            test.addOutcome(FAILED, abortOnError=True)
        return tx_recp

    def send_unsigned_transaction(self, test, web3, nonce, account, build_tx, persist_nonce, verbose=True):
        """Send an unsigned transaction to the network."""
        tx_hash = None
        try:
            tx_hash = web3.eth.send_transaction(build_tx)
            if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'SENT')
        except Exception as e:
            self.log.error('Error sending raw transaction %s', e)
            if persist_nonce: test.nonce_db.update(account.address, test.env, nonce, 'TIMEDOUT')
            test.addOutcome(BLOCKED, abortOnError=True)
        if verbose: self.log.info('Transaction sent with hash %s', tx_hash.hex())
        return tx_hash