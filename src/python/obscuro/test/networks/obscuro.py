import requests, json, os
from web3 import Web3
from obscuro.test.networks.default import Default
from obscuro.test.networks.geth import Geth
from obscuro.test.utils.properties import Properties
from eth_account.messages import encode_defunct
from web3.middleware import geth_poa_middleware


class ObscuroDefaultL1(Geth):
    """The Obscuro default L1 network. """
    ETH_LIMIT = 1
    ETH_ALLOC = 10

    def connect(self, test, private_key, web_socket=False, check_funds=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        account = web3.eth.account.privateKeyToAccount(private_key)
        test.log.info('Account %s connected to %s on %s' % (account.address, self.__class__.__name__, url))

        balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
        test.log.info('Account %s balance %.6f ETH' % (account.address, balance))
        if check_funds and balance < self.ETH_LIMIT:
            test.log.info('Account balance %.6f ETH below threshold %s, allocating more ...' % (balance, self.ETH_LIMIT))
            test.fund_eth(self, account, self.ETH_ALLOC, Properties().l1_funded_account_pk(test.env))
            test.log.info('Account new balance %.6f ETH' % web3.fromWei(web3.eth.get_balance(account.address), 'ether'))
        return web3, account


class ObscuroL1(ObscuroDefaultL1):
    """The L1 network for testnet. """
    HOST = 'http://testnet-eth2network.uksouth.azurecontainer.io'
    PORT = 8025
    WS_PORT = 9000


class ObscuroL1Dev(ObscuroDefaultL1):
    """The L1 network for dev-testnet. """
    HOST = 'http://dev-testnet-eth2network.uksouth.azurecontainer.io'
    PORT = 8025
    WS_PORT = 9000


class ObscuroL1Local(ObscuroDefaultL1):
    """The L1 network for a local testnet. """
    HOST = 'http://eth2network' if os.getenv('DOCKER_TEST_ENV') else 'http://127.0.0.1'
    PORT = 8025
    WS_PORT = 9000


class ObscuroL1Sim(ObscuroDefaultL1):
    """The L1 network for the dev simulation. """
    HOST = 'http://127.0.0.1'
    PORT = 37025
    WS_PORT = 37100


class Obscuro(Default):
    """The L2 network for all Obscuro modes (all go through the wallet extension). """
    HOST = 'http://127.0.0.1'
    WS_HOST = 'ws://127.0.0.1'
    PORT = None            # set by the factory for the wallet extension port of the accessing test
    WS_PORT = None         # set by the factory for the wallet extension port of the accessing test
    OBX_LIMIT = 10
    OBX_ALLOC = 100

    def chain_id(self): return 777

    def connect(self, test, private_key, web_socket=False, check_funds=True):
        url = self.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.privateKeyToAccount(private_key)
        self.__generate_viewing_key(web3, self.HOST, self.PORT, account, private_key)
        test.log.info('Account %s connected to %s on %s' % (account.address, self.__class__.__name__, url))

        balance = web3.fromWei(web3.eth.get_balance(account.address), 'ether')
        test.log.info('Account %s balance %.6f OBX' % (account.address, balance))
        if check_funds and balance < self.OBX_LIMIT:
            test.log.info('Account balance %.6f OBX below threshold %s, allocating more ...' % (balance, self.OBX_LIMIT))
            test.fund_obx(self, account, self.OBX_ALLOC)
            test.log.info('Account new balance %.6f OBX' % web3.fromWei(web3.eth.get_balance(account.address), 'ether'))
        return web3, account

    def __generate_viewing_key(self, web3, host, port, account, private_key):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        data = {"address": account.address}
        response = requests.post('%s:%d/generateviewingkey/' % (host, port), data=json.dumps(data), headers=headers)
        signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)

        data = {"signature": signed_msg.signature.hex(), "address": account.address}
        requests.post('%s:%d/submitviewingkey/' % (host, port), data=json.dumps(data), headers=headers)


