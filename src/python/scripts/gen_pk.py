# Utility script to create a private key and log the account address
#
import secrets
from web3 import Web3

for i in range(0,2):
    pk = secrets.token_hex(32)
    account = Web3().eth.account.from_key(pk)
    print('Private key: %s' % pk)
    print('Account adr: %s' % account.address)