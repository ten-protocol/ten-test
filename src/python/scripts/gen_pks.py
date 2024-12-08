# Utility script to create a private key and log the account address
#
import secrets
from web3 import Web3


pk = secrets.token_hex(32)
account = Web3().eth.account.from_key(pk)
print('FundAcntPK = %s' % pk)

for i in range(1,13):
    pk = secrets.token_hex(32)
    account = Web3().eth.account.from_key(pk)
    print('Account%dPK = %s' % (i, pk))
