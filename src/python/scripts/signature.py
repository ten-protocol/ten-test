from web3 import Web3

text='TwoIndexedAddresses(address,address);'
text='Guessed(address,uint256,bool,uint256);'
print(Web3.keccak(text=text).hex())