import secrets
from web3 import Web3

pk = secrets.token_hex(32)
account = Web3().eth.account.privateKeyToAccount(pk)
print('Private key: %s' % pk)
print('Account adr: %s' % account.address)