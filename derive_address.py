from web3 import Web3

# The private key from the properties file
private_key = '0x044288029c015996cc86a466be8493cd4eb35ae67d766e7ee4e85f808d15ffe3'

# Remove 0x prefix if present
if private_key.startswith('0x'):
    private_key = private_key[2:]

# Make sure we're using 0x prefix for the Web3 function
private_key_with_prefix = '0x' + private_key

try:
    # Create Web3 instance
    w3 = Web3()
    
    # Generate the account object from the private key
    account = w3.eth.account.from_key(private_key_with_prefix)
    
    # Print the result
    print(f"Private key: {private_key}")
    print(f"Address (public key): {account.address}")
except Exception as e:
    print(f"Error: {str(e)}") 