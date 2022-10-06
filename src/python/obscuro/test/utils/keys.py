from web3 import Web3


def pk_to_account(private_key):
    """Convert a private key to an account. """
    return Web3().eth.account.privateKeyToAccount(private_key)