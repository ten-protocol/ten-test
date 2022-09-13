from web3 import Web3
from ethsys.utils.properties import Properties
from ethsys.networks.default import Default


class Ropsten(Default):
    """A Ropsten node giving access to the underlying network."""
    HOST = 'ropsten.infura.io'

    @classmethod
    def chain_id(cls): return 3

    @classmethod
    def http_connection(cls, private_key, host, port):
        web3 = Web3(Web3.HTTPProvider('https://%s/v3/%s' % (host, Properties().infuraProjectID())))
        account = web3.eth.account.privateKeyToAccount(private_key)
        return web3, account




