Admin controls on Obscuro Testnet
=================================
This directory contains utilities to perform admin operations on Obscuro testnet. This is to;

- fund layer 1 distribution account and bridge tokens (`fund_layer_one`)
- fund layer 2 distribution account (`fund_layer_two`)
- fund test users in layer 2 with native OBX and HOC and POC (`fund_test_users`)
- fund community users in layer 2 with HOC and POC (`fund_users`)

For setup notes, see the top level [readme](../README.md)

Fund native ETH, HOC and POC tokens in the Layer 1
--------------------------------------------------
`fund_layer_one` performs a native ETH transfer from a pre-funded account on layer 1 to a distribution account. To 
perform this the private key of the pre-funded account must be known to the test framework and is configured in the 
`default.properties` file. The pre-funded account is also the holder of HOC and POC tokens on layer 1, as it is used 
to deploy these contracts. It is therefore additionally used to transfer tokens from the ERC20 contracts to the 
distribution account. This then allows transfer of the tokens to the bridge address so that they are available in 
layer 2. To run use;

```bash
# to run on Obscuro testnet 
pysys.py run fund_layer_one

# to run on Obscuro dev-testnet 
pysys.py run  -m obscuro.dev fund_layer_one

# to run on Obscuro local testnet 
pysys.py run  -m obscuro.local fund_layer_one
```

Fund native OBX in Layer 2
----------------------------------------------------
`fund_layer_two` performs a request to the faucet server for native OBX on behalf of the distribution account.  It 
additionally prints out the token balances for HOC and POC in layer 2 for reference. Note that when running on a local 
testnet no faucet server is available, and a native transfer from the pre-funded account on layer 2 to the distribution 
account is used instead. To run use;

```bash
# to run on Obscuro testnet 
pysys.py run fund_layer_two

# to run on Obscuro dev-testnet 
pysys.py run -m obscuro.dev fund_layer_two

# to run on Obscuro local testnet 
pysys.py run  -m obscuro.local fund_layer_two
```

Funding test users
------------------
`fund_test_users` performs a transfer of native OBX, and HOC and POC tokens to each of the test accounts used within the 
`obscuro-test` testcases. To run use;

```bash
# to run on Obscuro testnet to allocate funds
pysys.py run fund_test_users

# to run on Obscuro dev-testnet to allocate funds
pysys.py run -m obscuro.dev fund_test_users

# to run on Obscuro local testnet 
pysys.py run  -m obscuro.local fund_test_users
```

Funding users
-------------
`fund_users` performs a transfer of HOC and POC tokens to each of the community registered accounts. 
To run use;

```bash
# to run on Obscuro testnet 
pysys.py run fund_users

# to run on Obscuro dev-testnet 
pysys.py run -m obscuro.dev fund_users

# to run on Obscuro local testnet 
pysys.py run  -m obscuro.local fund_users
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



