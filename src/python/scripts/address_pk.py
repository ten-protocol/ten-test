# Utility script to show the address for a pk
#
from web3 import Web3

pk = "01f854ffc77fc0c1300247d84f0c0979f6e74d5913c889c7a7fc27909861bc51"
account = Web3().eth.account.privateKeyToAccount(pk)
print('Private key: %s' % pk)
print('Address is: %s' % account.address)
