import requests, json, os
from web3 import Web3
from obscuro.test.networks.default import Default
from obscuro.test.networks.geth import Geth
from eth_account.messages import encode_defunct


class ObscuroL1(Geth):
    HOST = 'http://testnet-gethnetwork.uksouth.azurecontainer.io'
    PORT = 8025
    WS_PORT = 9000


class ObscuroL1Dev(Geth):
    HOST = 'http://dev-testnet-gethnetwork.uksouth.azurecontainer.io'
    PORT = 8025
    WS_PORT = 9001


class ObscuroL1Local(Geth):
    HOST = 'http://gethnetwork' if os.getenv('DOCKER_TEST_ENV') else 'http://127.0.0.1'
    PORT = 8025
    WS_PORT = 9002


class ObscuroL1Sim(Geth):
    HOST = 'http://127.0.0.1'
    PORT = 37025
    WS_PORT = 37100


class Obscuro(Default):
    """The Obscuro wallet extension giving access to the underlying network."""
    HOST = 'http://127.0.0.1'
    WS_HOST = 'ws://127.0.0.1'
    PORT = None            # set by the factory for the wallet extension port of the accessing test
    WS_PORT = None         # set by the factory for the wallet extension port of the accessing test

    @classmethod
    def chain_id(cls):
        return 777

    @classmethod
    def connect(cls, test, private_key, web_socket=False):
        url = cls.connection_url(web_socket)

        if not web_socket: web3 = Web3(Web3.HTTPProvider(url))
        else: web3 = Web3(Web3.WebsocketProvider(url, websocket_timeout=120))
        account = web3.eth.account.privateKeyToAccount(private_key)
        cls.__generate_viewing_key(web3, cls.HOST, cls.PORT, account, private_key)
        test.log.info('Account %s connected to %s on %s' % (account.address, cls.__name__, url))
        return web3, account

    @classmethod
    def __generate_viewing_key(cls, web3, host, port, account, private_key):
        # generate a viewing key for this account, sign and post it to the wallet extension
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        data = {"address": account.address}
        response = requests.post('%s:%d/generateviewingkey/' % (host, port), data=json.dumps(data), headers=headers)
        signed_msg = web3.eth.account.sign_message(encode_defunct(text='vk' + response.text), private_key=private_key)

        data = {"signature": signed_msg.signature.hex(), "address": account.address}
        requests.post('%s:%d/submitviewingkey/' % (host, port), data=json.dumps(data), headers=headers)


