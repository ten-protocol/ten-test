Admin controls on Obscuro Testnet
=================================
This directory contains utilities to perform admin operations on Obscuro testnet. Currently, this is to;

- deploy a set of contracts that can be used across different tests (`deploy_contracts`)
- reset all persisted nonce db entries for test users (`persistence_reset`)
- print user balances on L2 (`print_balances`)


Managing the nonce db on a new deployment 
-----------------------------------------
We do not use `eth_get_transaction_count` in order to determine a nonce to use in a particular transaction, but use local
persisted storage maintained by the test framework. On a new clone of the test framework, we need to bring the persistence
inline with the latest known transaction count (assuming no transactions in the pending state). The `persistence_reset` 
script will perform both functions; delete all entries for a given environment and update for the latest transaction
count. It should be run after a new clone of the framework using;

```bash
# to clear all persisted nonces for Obscuro testnet 
pysys.py run persistence_reset

# to clear all persisted nonces for Obscuro dev-testnet 
pysys.py run  -m obscuro.dev persistence_reset

# to clear all persisted nonces for Obscuro local testnet 
pysys.py run  -m obscuro.local persistence_reset
```
