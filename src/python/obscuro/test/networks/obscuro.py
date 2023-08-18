import requests, json
from web3 import Web3
from obscuro.test.networks.default import Default
from obscuro.test.networks.geth import Geth
from obscuro.test.utils.properties import Properties
from eth_account.messages import encode_defunct
from web3.middleware import geth_poa_middleware
from obscuro.test.helpers.wallet_extension import WalletExtension


class ObscuroL1(Geth):
    """The Obscuro L1 connection. """
    ETH_LIMIT = 1
    ETH_ALLOC = 10

    def __init__(self, test, name):
        super().__init__(test, name)
        props = Properties()
        self.HOST = props.l1_host_http(test.env)
        self.WS_HOST = props.l1_host_ws(test.env)
        self.PORT = props.l1_port_http(test.env)
        self.WS_PORT = props.l1_port_ws(test.env)
        self.CHAIN_ID = props.chain_id(test.env)

    def connect(self, test, private_key, web_socket=False, check_funds=True, log=True, **kwargs):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        account = web3.eth.account.privateKeyToAccount(private_key)
        if log: test.log.info('Account %s connected to %s on %s', account.address, self.__class__.__name__, url)

        if check_funds:
            balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
            if balance < self.ETH_LIMIT:
                if log: test.log.info('Account balance %.6f ETH below threshold %s', balance, self.ETH_LIMIT)
                test.fund_native(self, account, self.ETH_ALLOC, Properties().l1_funded_account_pk(test.env), persist_nonce=False)
            if log: test.log.info('Account balance %.6f ETH', web3.fromWei(web3.eth.get_balance(account.address), 'ether'))
        return web3, account


class Obscuro(Default):
    """The L2 connection for Obscuro. """
    OBX_LIMIT = 0.5
    OBX_ALLOC = 1
    CURRENCY = 'OBX'

    def __init__(self, test, name):
        super().__init__(test, name)
        props = Properties()

        # run a wallet extensions locally to override
        wallet_extension = WalletExtension(test, name=name)
        wallet_extension.run()
        self.HOST = 'http://127.0.0.1'
        self.WS_HOST = 'ws://127.0.0.1'
        self.PORT = wallet_extension.port
        self.WS_PORT = wallet_extension.ws_port
        self.CHAIN_ID = props.chain_id(test.env)

    def connect(self, test, private_key, web_socket=False, check_funds=True, log=True, **kwargs):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.privateKeyToAccount(private_key)
        self.__generate_viewing_key(web3, self.HOST, self.PORT, account, private_key)
        if log: test.log.info('Account %s connected to %s on %s', account.address, self.__class__.__name__, url)

        if check_funds:
            balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
            if balance < self.OBX_LIMIT:
                if log: test.log.info('Account balance %.6f OBX below threshold %s', balance, self.OBX_LIMIT)
                test.distribute_native(account, self.OBX_ALLOC)
            if log: test.log.info('Account balance %.6f OBX', web3.fromWei(web3.eth.get_balance(account.address), 'ether'))
        return web3, account

    @staticmethod
    def __generate_viewing_key(web3, host, port, account, private_key):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        data = {"address": account.address}
        response = requests.post('%s:%d/generateviewingkey/' % (host, port), data=json.dumps(data), headers=headers)
        signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)

        data = {"signature": signed_msg.signature.hex(), "address": account.address}
        requests.post('%s:%d/submitviewingkey/' % (host, port), data=json.dumps(data), headers=headers)


