from web3 import Web3

text='Guessed(address,uint256,bool,uint256)'
text='Attempts(address,uint256)'
text='Stored(uint256)'
text='TwoIndexedAddresses(address,address)'

print(Web3.keccak(text=text).hex())