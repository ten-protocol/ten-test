Admin controls on Obscuro Testnet
=================================
This directory contains utilities to perform admin operations on Obscuro testnet. This is to;

- fund native tokens into the layer 2 for OBX for the deployment account (`fund_deploy_native`)
- fund ERC20 tokens into the layer 2 for HOC / POC for the deployment account (`fund_deploy_tokens`)
- fund a test user with HOC, POC and native OBX tokens (`fund_test_users`)
- fund a user with HOC, POC and native OBX tokens (`fund_users`)

For setup notes, see the top level [readme](../README.md)

Funds native OBX into the Layer 2
---------------------------------
`fund_deploy_native` provides the ability to ensure the native OBX required for transaction gas costs in the pre-funded 
deployment account in layer 2 do not fall below a certain threshold. When the amount falls below the threshold it is 
increased back up to the target amount. Funding is via transferring from the faucet account to the deployment account. 
To run a check and perform an allocation use;

```bash
# to run on Obscuro testnet 
pysys.py run fund_deploy_native

# to run on Obscuro dev-testnet 
pysys.py run -m obscuro.dev fund_deploy_native
```

Funds tokens into the Layer 2
-----------------------------
`fund_deploy_tokens` provides the ability to ensure the tokens in the pre-funded deployment account in layer 2 do not 
fall below a certain threshold. When the token amount falls below the threshold it is increased back up to the target 
amount. Funding is via transferring from layer 1 to the bridge address which then automatically syncs across into the 
layer 2. To run a check and perform an allocation use;

```bash
# to run on Obscuro testnet 
pysys.py run fund_deploy_tokens

# to run on Obscuro dev-testnet 
pysys.py run -m obscuro.dev fund_deploy_tokens
```

Funding test users
------------------
`fund_test_users` provides the ability to ensure the native OBX, HOC and POC tokens for all test users in layer 2 do not
fall below a certain threshold. To run a check and perform an allocation use;

```bash
# to run on Obscuro testnet to display balances only
pysys.py run -XDISPLAY fund_test_users

# to run on Obscuro testnet to allocate funds
pysys.py run fund_test_users

# to run on Obscuro dev-testnet to allocate funds
pysys.py run -m obscuro.dev fund_test_users
```

Funding users
-------------
`fund_users` provides the ability to add in new user accounts, and for them to be allocated native OBX, HOC and POC 
tokens. To transfer tokens to an account address use;

```bash
# to run on Obscuro testnet 
pysys.py run fund_users

# to run on Obscuro dev-testnet 
pysys.py run -m obscuro.dev fund_users
```

At the moment accounts managed are defined in the `fund_users/run.py` script, as a list of account addresses. Due to 
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



