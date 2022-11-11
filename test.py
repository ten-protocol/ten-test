import requests, json


# serveMux.HandleFunc(pathAPI+pathNumRollups, o.getNumRollups)            // Get the number of published rollups.
# serveMux.HandleFunc(pathAPI+pathNumTxs, o.getNumTransactions)           // Get the number of rolled-up transactions.
# serveMux.HandleFunc(pathAPI+pathGetRollupTime, o.getRollupTime)         // Get the average rollup time.
# serveMux.HandleFunc(pathAPI+pathLatestRollups, o.getLatestRollups)      // Get the latest rollup numbers.
# serveMux.HandleFunc(pathAPI+pathLatestTxs, o.getLatestTxs)              // Get the latest transaction hashes.
# serveMux.HandleFunc(pathAPI+pathRollup, o.getRollupByNumOrTxHash)       // Get the rollup given its number or the hash of a transaction it contains.
# serveMux.HandleFunc(pathAPI+pathBlock, o.getBlock)                      // Get the L1 block with the given number.
# serveMux.HandleFunc(pathAPI+pathDecryptTxBlob, o.decryptTxBlob)         // Decrypt a transaction blob.
# serveMux.HandleFunc(pathAPI+pathAttestation, o.attestation)             // Retrieve the node's attestation.
# serveMux.HandleFunc(pathAPI+pathAttestationReport, o.attestationReport) // Retrieve the node's attestation report.

# 1. GetHeadRollupHeader   = "obscuroscan_getHeadRollupHeader"
# 2. GetTotalTxs           = "obscuroscan_getTotalTransactions"       // the total number of transactions on obx
# 3. GetLatestTxs          = "obscuroscan_getLatestTransactions"      // return x latest transactions
# 4. GetRollupForTx        = "obscuroscan_getRollupForTx"             // return rollup that contains a transaction
# 5. GetBlockHeaderByHash  = "obscuroscan_getBlockHeaderByHash"       // return L1 block by its hash
# 6. Attestation           = "obscuroscan_attestation"                // return the nodes attestation
# 7. GetRollup             = "obscuroscan_getRollup"                  //


print("1. ")
print("***** o.getNumRollups, o.getRollupTime")
data_getHeadRollupHeader = {"jsonrpc": "2.0", "method": "obscuroscan_getHeadRollupHeader", "params": [], "id": 1 }
response = requests.post("http://testnet.obscu.ro:13000", json=data_getHeadRollupHeader)
print('output', response.json())

print("2. ")
print("***** o.getNumTransactions")
data_getTotalTransactions = {"jsonrpc": "2.0", "method": "obscuroscan_getTotalTransactions", "params": [], "id": 1 }
response = requests.post("http://testnet.obscu.ro:13000", json=data_getTotalTransactions)
print('output', response.json())

print("3. ")
print("***** o.getLatestTxs")
data_getLatestTransactions = {"jsonrpc": "2.0", "method": "obscuroscan_getLatestTransactions", "params": [5], "id": 3 }
response = requests.post("http://testnet.obscu.ro:13000", json=data_getLatestTransactions)
print('output', response.json())

print("4. ")
print("***** o.getRollupByNumOrTxHash")
data_getRollupByNumOrTxHash = {"jsonrpc": "2.0", "method": "obscuroscan_getRollupForTx", "params": ["0xb901925d951b16b474d2ae95be6721a05a5b47bd62d96487a30714257efc85da"], "id": 4 }
response = requests.post("http://testnet.obscu.ro:13000", json=data_getRollupByNumOrTxHash)
l1Proof = response.json()["result"]["Header"]["L1Proof"]
encryptedTxBlob = response.json()["result"]["EncryptedTxBlob"]
print('output', json.dumps(response.json(), indent=2))

print("5. ")
print("***** o.getBlock")
data_getBlockHeaderByHash = {"jsonrpc": "2.0", "method": "obscuroscan_getBlockHeaderByHash", "params": [l1Proof], "id": 5 }
response = requests.post("http://testnet.obscu.ro:13000", json=data_getBlockHeaderByHash)
print('output', json.dumps(response.json(), indent=2))

print("6. ")
print("***** o.attestation")
data_attestation = {"jsonrpc": "2.0", "method": "obscuroscan_attestation", "params": [], "id": 6 }
response = requests.post("http://testnet.obscu.ro:13000", json=data_attestation)
print('output', json.dumps(response.json(), indent=2))



