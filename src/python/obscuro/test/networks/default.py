from web3 import Web3
from pysys.constants import *
from obscuro.test.utils.properties import Properties

class Default:
    """A default node giving access to an underlying network."""
    HOST = 'http://127.0.0.1'
    WS_HOST = 'ws://127.0.0.1'
    PORT = 8545
    WS_PORT = 8545

    @classmethod
    def chain_id(cls): return None

    @classmethod
    def connection_url(cls, web_socket=False):
        port = cls.PORT if not web_socket else cls.WS_PORT
        host = cls.HOST if not web_socket else cls.WS_HOST
        return '%s:%d' % (host, port)

    @classmethod
    def connect(cls, test, private_key, web_socket=False):
        url = cls.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.privateKeyToAccount(private_key)
        test.log.info('Account %s connected to %s on %s' % (account.address, cls.__name__, url))
        return web3, account

    @classmethod
    def connect_account1(cls, test, web_socket=False):
        return cls.connect(test, Properties().account1pk(), web_socket)

    @classmethod
    def connect_account2(cls, test, web_socket=False):
        return cls.connect(test, Properties().account2pk(), web_socket)

    @classmethod
    def connect_account3(cls, test, web_socket=False):
        return cls.connect(test, Properties().account3pk(), web_socket)

    @classmethod
    def connect_account4(cls, test, web_socket=False):
        return cls.connect(test, Properties().account4pk(), web_socket)

    @classmethod
    def transact(cls, test, web3, target, account, gas_limit):
        remote_nonce = web3.eth.get_transaction_count(account.address)
        local_nonce = test.nonce_db.get_nonce(account.address, test.env)+1

        nonce = remote_nonce
        if remote_nonce == 0: test.nonce_db.delete(account.address, test.env)  # new environment
        if remote_nonce >= local_nonce: nonce = remote_nonce                   # new test deployment
        else: nonce = local_nonce                                              # likely pending transactions

        test.log.info('Account %s remote %s, local %d, using %d' % (account.address, remote_nonce, local_nonce, nonce))
        test.nonce_db.insert(account.address, test.env, nonce)

        tx_sign = cls.build_transaction(test, web3, target, nonce, account, gas_limit)
        test.nonce_db.update(account.address, test.env, nonce, 'SIGNED')

        tx_hash = cls.send_transaction(test, web3, tx_sign)
        test.nonce_db.update(account.address, test.env, nonce, 'SENT')

        tx_recp = cls.wait_for_transaction(test, web3, tx_hash)
        test.nonce_db.update(account.address, test.env, nonce, 'CONFIRMED')
        return tx_recp

    @classmethod
    def build_transaction(cls, test, web3, target, nonce, account, gas_limit):
        build_tx = target.buildTransaction(
            {
                'nonce': nonce,
                'gasPrice': 1000,             # the price we are willing to pay per gas unit (dimension is gwei)
                'gas': gas_limit,             # max gas units prepared to pay (dimension is computational units)
                'chainId': web3.eth.chain_id
            }
        )
        signed_tx = account.sign_transaction(build_tx)
        return signed_tx

    @classmethod
    def send_transaction(cls, test, web3, signed_tx):
        tx_hash = None
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        except Exception as e:
            test.log.error('Error sending raw transaction %s' % e)
            test.addOutcome(BLOCKED, abortOnError=True)
        test.log.info('Transaction sent with hash %s' % tx_hash.hex())
        return tx_hash

    @classmethod
    def wait_for_transaction(cls, test, web3, tx_hash):
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            test.log.info('Transaction receipt block hash %s' % tx_receipt.blockHash.hex())
        else:
            test.log.error('Transaction receipt failed')
            test.log.error('Full receipt: %s' % tx_receipt)
            test.addOutcome(FAILED, abortOnError=True)
        return tx_receipt
