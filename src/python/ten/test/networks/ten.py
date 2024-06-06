import requests, json
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3.middleware import geth_poa_middleware
from pysys.constants import BLOCKED
from ten.test.networks.default import DefaultPreLondon
from ten.test.networks.geth import Geth
from ten.test.networks.sepolia import Sepolia
from ten.test.utils.properties import Properties
from ten.test.helpers.wallet_extension import WalletExtension


class TenL1Sepolia(Sepolia):
    """The Ten L1 Sepolia implementation connection. """
    ETH_LIMIT = 0.02
    ETH_ALLOC = 0.05
    ETH_ALLOC_EPHEMERAL = 0.005

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.l1_host_http(test.env)
        self.WS_HOST = props.l1_host_ws(test.env)
        self.PORT = props.l1_port_http(test.env)
        self.WS_PORT = props.l1_port_ws(test.env)
        self.CHAIN_ID = props.chain_id(test.env)

    def connection_url(self, web_socket=False):
        return '%s/%s' % (self.HOST if not web_socket else self.WS_HOST, Properties().sepoliaAPIKey())

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.from_key(private_key)
        balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
        if verbose: self.log.info('Account %s connected to %s (%.6f ETH)', account.address, self.__class__.__name__, balance)

        if check_funds and balance < self.ETH_LIMIT:
            if verbose: self.log.info('Account %s balance is below threshold %s ... need to distribute funds', account.address, self.ETH_LIMIT)
            test.fund_native(self, account, self.ETH_ALLOC, Properties().l1_funded_account_pk(test.env), persist_nonce=False)
            if verbose:
                balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
                self.log.info('Account %s balance is now %.6f ETH', account.address, balance)
        return web3, account


class TenL1Geth(Geth):
    """The Ten L1 Geth implementation connection. """
    ETH_LIMIT = 0.5
    ETH_ALLOC = 1.0
    ETH_ALLOC_EPHEMERAL = 0.01

    def __init__(self, test, name=None, **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.HOST = props.l1_host_http(test.env)
        self.WS_HOST = props.l1_host_ws(test.env)
        self.PORT = props.l1_port_http(test.env)
        self.WS_PORT = props.l1_port_ws(test.env)
        self.CHAIN_ID = props.chain_id(test.env)

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        account = web3.eth.account.from_key(private_key)
        balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
        if verbose: self.log.info('Account %s connected to %s (%.6f ETH)', account.address, self.__class__.__name__, balance)

        if check_funds and balance < self.ETH_LIMIT:
            if verbose: self.log.info('Account %s balance is below threshold %s ... need to distribute funds', account.address, self.ETH_LIMIT)
            test.fund_native(self, account, self.ETH_ALLOC, Properties().l1_funded_account_pk(test.env),
                             persist_nonce=False, gas_limit=21000)
            if verbose:
                balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
                self.log.info('Account %s balance is now %.6f ETH', account.address, balance)
        return web3, account


class Ten(DefaultPreLondon):
    """The L2 connection for Ten.

    A ten network instance requires a wallet extension (gateway) to connect to the network. A gateway can support
    multiple connections through joining as a particular user_id, under which multiple accounts can be registered.
    When creating an instance of the connection, the name indicates the gateway instance to use. Tests have the
    notion of a primary gateway, which on a local testnet is locally started, and on a remote network (dev|uat|sepolia)
    is the hosted gateway on that environment. If the name 'primary' is supplied in the connection creation then this
    instance is used (and locally started for a local testnet). If any other name is supplied then a local gateway
    instance is started. If the name supplied already exists, the pre-existing instance of that gateway will be used.
    """
    ETH_LIMIT = 0.1
    ETH_ALLOC = 0.5

    def __init__(self, test, name='primary', **kwargs):
        super().__init__(test, name, **kwargs)
        props = Properties()
        self.CHAIN_ID = props.chain_id(test.env)

        if name in test.connections:
            self.HOST = test.connections[name][0]
            self.WS_HOST = test.connections[name][1]
            self.PORT = test.connections[name][2]
            self.WS_PORT = test.connections[name][3]
            self.log.info('Using existing gateway %s on host=%s, port=%d', name, self.HOST, self.PORT)

        else:
            if name == 'primary':
                self.HOST = props.host_http(test.env)
                self.WS_HOST = props.host_ws(test.env)
                self.PORT = props.port_http(test.env)
                self.WS_PORT = props.port_ws(test.env)
                self.log.info('Using primary gateway on host=%s, port=%d', self.HOST, self.PORT)
            else:
                wallet = WalletExtension.start(test, name=name)
                self.PORT = 'http://127.0.0.1'
                self.WS_PORT = 'ws://127.0.0.1'
                self.PORT = wallet.port
                self.WS_PORT = wallet.ws_port
                self.log.info('Using local gateway %s on host=%s, port=%d', name, self.HOST, self.PORT)

            test.connections[name] = (self.HOST, self.WS_HOST, self.PORT, self.WS_PORT)

        self.ID = self.__join()
        if self.ID is None:
            test.addOutcome(BLOCKED, 'Error joining network for connection', abortOnError=True)

    def connection_url(self, web_socket=False):
        port = self.PORT if not web_socket else self.WS_PORT
        host = self.HOST if not web_socket else self.WS_HOST
        return '%s:%d/v1/?token=%s' % (host, port, self.ID)

    def connect(self, test, private_key, web_socket=False, check_funds=True, verbose=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.from_key(private_key)
        self.__register(test, account)
        balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
        if verbose: self.log.info('Account %s connected to %s (%.6f ETH), wss=%s', account.address, self.__class__.__name__, balance, web_socket)

        if check_funds and balance < self.ETH_LIMIT:
            if verbose: self.log.info('Account %s balance is below threshold %s ... need to distribute funds', account.address, self.ETH_LIMIT)
            test.distribute_native(account, self.ETH_ALLOC)
            if verbose:
                balance = web3.from_wei(web3.eth.get_balance(account.address), 'ether')
                self.log.info('Account %s balance is now %.6f ETH', account.address, balance)
        return web3, account

    def __join(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = requests.get('%s:%d/v1/join/' % (self.HOST, self.PORT),  headers=headers)
        if response.ok: return response.text.strip()
        return None

    def __register(self, test, account):
        domain = {'name': 'Ten', 'version': '1.0', 'chainId': Properties().chain_id(test.env)}
        types = {
            'Authentication': [
                {'name': 'Encryption Token', 'type': 'address'},
            ],
        }
        message = {'Encryption Token': "0x"+self.ID}

        signable_msg_from_dict = encode_typed_data(domain, types, message)
        signed_msg_from_dict = Account.sign_message(signable_msg_from_dict, account.key)

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"signature": signed_msg_from_dict.signature.hex(), "address": account.address}
        requests.post('%s:%d/v1/authenticate/?token=%s' % (self.HOST, self.PORT, self.ID),
                      data=json.dumps(data), headers=headers)

    def __register_new(self, test, account):
        url = '%s:%d/v1/getmessage/' % (self.HOST, self.PORT)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"encryptionToken": self.ID, "formats": ["EIP712"]}
        response = requests.get(url, headers=headers, json=data).text
        message = json.loads(response)["message"]

        signable_msg_from_dict = encode_typed_data(message["domain"], message["types"], message["message"])
        signed_msg_from_dict = Account.sign_message(signable_msg_from_dict, account.key)

        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        data = {"signature": signed_msg_from_dict.signature.hex(), "address": account.address}
        requests.post('%s:%d/v1/authenticate/?token=%s' % (self.HOST, self.PORT, self.ID),
                      data=json.dumps(data), headers=headers)

