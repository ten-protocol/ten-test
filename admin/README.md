Admin controls on Obscuro TestNet
=================================
This directory contains utilities to perform admin operations on the Obscuro Testnet. This is to 

- allocate funds into the layer 2 into the OBX ERC20 contract for use by the number guessing game
- transfer funds into a user who wishes to play the number guessing game
- transfer funds into test users for running end to end tests

For setup notes, see the top level [readme](../README.md)

Funding the faucet
------------------
`fund_faucet` provides the ability to ensure the tokens in the pre-funded deployment account (the owner of the OBX ERC20
token contract) in layer 2 do not fall below a certain threshold (currently set at 1000). When the token amount falls 
below this amount it is increased back up to 1000000. To run a check and perform an allocation if required used;

```bash
pysys.py run fund_faucet
```

Funding users
-------------
`fund_user` provides the ability to add in new user accounts, and for them to be allocated a token amount (current 
set to 50 tokens). To transfer 50 tokens to an account address use;

```bash
pysys.py run fund_user
```

At the moment accounts managed are defined in the `fund_user/run.py` script, as a list of account addresses. Due to 
privacy built into the ERC20 contract, it is not possible for an admin to see token balances for an account they do not 
hold a private key to. As such any account address in the list will be allocated 50 tokens on running. To add a new 
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



