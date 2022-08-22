Admin controls on Obscuro TestNet
=================================
This directory contains utilities to perform admin operations on Obscuro. This is to;

- fund tokens into the layer 2 for the HOC and POC ERC20 contracts
- fund a user with HOC, POC and native OBX tokens 
- fund a test user with HOC, POC and native OBX tokens for running end-to-end tests

For setup notes, see the top level [readme](../README.md)

Funds tokens into the Layer 2
-----------------------------
`fund_tokens` provides the ability to ensure the tokens in the pre-funded deployment account (the owner of the HOC and 
POC ERC20 token contracts) in layer 2 do not fall below a certain threshold. When the token amount falls below the 
threshold it is increased back up to the target amount. Funding is via transferring from layer 1 to the bridge address
which then automatically syncs across into the layer 2. To run a check and perform an allocation use;

```bash
# to run on Obscuro testnet 
pysys.py run fund_tokens

# to run on Obscuro dev-testnet 
pysys.py run -m obscuro.dev fund_tokens
```

Funding users
-------------
`fund_user` provides the ability to add in new user accounts, and for them to be allocated HOC and POC tokens, as well 
as native OBX. To transfer tokens to an account address use;

```bash
# to run on Obscuro testnet 
pysys.py run fund_user

# to run on Obscuro dev-testnet 
pysys.py run -m obscuro.dev fund_user
```

At the moment accounts managed are defined in the `fund_user/run.py` script, as a list of account addresses. Due to 
privacy built into the ERC20 contract, it is not possible for an admin to see token balances for an account they do not 
hold a private key to. As such any account address in the list will be allocated set tokens on running. To add a new 
account address edit this file to add in the address to the USERS list and comment out any that should not have an 
allocation performed; 

```python
    USERS = [
        #'0x686Ad719004590e98F182feA3516d443780C64a1',
        #'0x85E1Cc949Bca27912e3e951ad1F68afD1cc4aB15',
        '0x61f991693aee28dbF4B7CBBB0ACf53ea92F219a3'
    ]
    AMOUNT = 50
```



