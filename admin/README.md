Admin controls on Obscuro Testnet
=================================
This directory contains utilities to perform admin operations on Obscuro testnet. This is to;

- delete and reset all persisted nonce db entries for test users (`persistence_reset`)
- fund layer 1 distribution and test user accounts with ETH (`fund_layer_one`)
- fund layer 2 distribution and test user accounts with OBX (`fund_layer_two`)

For setup notes, see the top level [readme](../README.md)


Managing the nonce db on a new deployment 
-----------------------------------------
We do not use `eth_get_transaction_count` in order to determine a nonce to use in a particular transaction, but use local
persisted storage maintained by the test framework. As we currently do not run against a persisted L1 or L2, on a new 
deployment we must clear out the persisted nonce database in order to reset the nonce's to zero (they need to monotonically 
increase). Additionally, on a new clone of the test framework, we need to bring the persistence inline with the latest 
known transaction count (assuming no transactions in the pending state). The `persistence_reset` script will perform both 
functions; delete all entries for a given environment and update for the latest transaction count. It should be run 
after a new deployment or clone of the framework using;

```bash
# to clear all persisted nonces for Obscuro testnet 
pysys.py run persistence_reset

# to clear all persisted nonces for Obscuro dev-testnet 
pysys.py run  -m obscuro.dev persistence_reset

# to clear all persisted nonces for Obscuro local testnet 
pysys.py run  -m obscuro.local persistence_reset
```

Fund native ETH in the Layer 1
--------------------------------------------------
`fund_layer_one` performs a native ETH transfer from a pre-funded account on layer 1 to a distribution account, and to 
all test user accounts. To perform this the private key of the pre-funded account must be known to the test framework 
and is configured in the `default.properties` file. To run use;

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
`fund_layer_two` performs a request to the faucet server for native OBX on behalf of the distribution account, and all 
test user accounts. Note that when running on a local testnet a native transfer from the pre-funded account on 
layer 2 to the account is used instead. To run use;

```bash
# to run on Obscuro testnet 
pysys.py run fund_layer_two

# to run on Obscuro dev-testnet 
pysys.py run -m obscuro.dev fund_layer_two

# to run on Obscuro local testnet 
pysys.py run  -m obscuro.local fund_layer_two
```


