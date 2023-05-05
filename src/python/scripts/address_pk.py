# Utility script to show the address for a pk
#
from web3 import Web3

pk = "69b32fb4662704820404866d4a4c9b2fcc8b4a796121939117b9cbb3ededb701"
account = Web3().eth.account.privateKeyToAccount(pk)
print('Private key: %s' % pk)
print('Address is: %s' % account.address)
