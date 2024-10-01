from web3 import Web3

text='TwoIndexedAddresses(address,address);'
print(Web3.keccak(text=text).hex())