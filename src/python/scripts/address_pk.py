# Utility script to show the address for a pk
#
from web3 import Web3

pk = "<the private key>"
account = Web3().eth.account.privateKeyToAccount(pk)
print('Private key: %s' % pk)
print('Address is: %s' % account.address)
