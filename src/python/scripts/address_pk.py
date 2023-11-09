# Utility script to show the address for a pk
#
from web3 import Web3

pk = "db7c08fd18fa350c104b5eb33ec2b5d9cdf7b595acf7f6b21d0f360dd9b621d7"
account = Web3().eth.account.privateKeyToAccount(pk)
print('Private key: %s' % pk)
print('Address is: %s' % account.address)
