const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')
const merkle = require('@openzeppelin/merkle-tree')
const { decode } = require("@ethereumjs/rlp");
require('console-stamp')(console, 'HH:MM:ss')

let MSG_ID = 1

/** Sleep utility to pause for a set number of ms */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/** Decode a base 64 string to the underlying object */
function decode_base64(base64String) {
  let jsonString = atob(base64String);
  return JSON.parse(jsonString);
}

/**  Process a value transfer event extracted from a tx receipt */
function process_log_message(value_transfer) {
  const abiTypes = ['address', 'address', 'uint256', 'uint64'];
  const msg = [
    value_transfer['args'].sender, value_transfer['args'].receiver,
    value_transfer['args'].amount.toString(), value_transfer['args'].sequence.toString()
  ]
  const abiCoder = new ethers.utils.AbiCoder()
  const encodedMsg = abiCoder.encode(abiTypes, msg)
  return [msg, ethers.utils.keccak256(encodedMsg)]
}

/** Get the xchain proof from the node */
async function tenGetXchainProof(node_url, type, msgHash) {
    const data = {jsonrpc: "2.0", method: "ten_getCrossChainProof", params: [type, msgHash], id: MSG_ID++}
    try {
        const response = await fetch(node_url, {
            method: "POST",
            headers: { "Content-Type": "application/json", },
            body: JSON.stringify(data),
        })
        const result = await response.json();
        if (result.result) {
            console.log(`Received root and proof:`)
            console.log(`  Proof = ${result.result.Proof}`)
            console.log(`  Root  = ${result.result.Root}`)
            return [result.result.Proof, result.result.Root]
        } else if (result.error) {
            console.info(`Error getting proof, reason = ${result.error.message}`)
        }
    } catch (error) {
        console.error("Error making RPC call:", error);
        return [null, null];
    }
    return [null, null]
}

/** Logic on the L2 side to initiate the transfer of funds to the L1 */
async function sendTransfer(provider, wallet, to, amount, bridge, bus) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await bridge.estimateGas.sendNative(to, { value: amount } );
  const currentNonce = await provider.getTransactionCount(wallet.address);
  console.log(`  Nonce:         ${currentNonce}`)

  // send an initial transaction in that we wont follow up with
  const tx0 = await bridge.populateTransaction.sendNative(to, {
      value: amount,
      gasPrice: gasPrice,
      gasLimit: estimatedGas,
      nonce: currentNonce}
  )
  const txResponse0 = await wallet.sendTransaction(tx0)

  // send a second transaction, and process the xchain tree for this one
  const tx = await bridge.populateTransaction.sendNative(to, {
      value: amount,
      gasPrice: gasPrice,
      gasLimit: estimatedGas,
      nonce: currentNonce + 1}
  )
  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent:     ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(`Transaction received: ${txReceipt.transactionHash}`)

  const block = await provider.send('eth_getBlockByHash', [txReceipt.blockHash, true]);
  console.log(`Block received:       ${block.number}`)

  // extract and log all the values
  const log_message = bus.interface.parseLog(txReceipt.logs[0]);
  const _processed_log_message = process_log_message(log_message)
  const msg = _processed_log_message[0]
  const msgHash = _processed_log_message[1]
  console.log(`  VTrans Hash:   ${msgHash}`)

  // return the msg, its hash, and the xchain tree root hash
  return [msg, msgHash]
}

/** Utility function to wait for the root and proof to be established from the node */
async function waitForRootPublished(node_url, msgHash, interval = 5000, timeout = 2400000) {
  var root = null
  var proof = null
  const startTime = Date.now();

  while (root === null) {
    try {
       const result = await tenGetXchainProof(node_url, 'v', msgHash)
       root = result[1]
       if (root !== null) {
           if (result[0] == null) {
             proof = []
             console.log('Proof was null so setting to empty list')
           }
           else {
               proof = decode(Buffer.from(result[0].slice(2), "hex"));
               console.log(`  Decoded Proof  = ${proof}`)
           }
       }
    } catch (error) {
      console.log(`waitForRootPublished error : ${error}`)
    }
    if (Date.now() - startTime >= timeout) {
      console.log(`Timed out waiting for for the root to be published`)
      break
    }
    await sleep(interval);
  }
  return [proof, root]
}

/** Logic on the L1 side to instruct the management contract to release funds */
async function extractNativeValue(provider, wallet, management, msg, proof, root) {
  const gasPrice = await provider.getGasPrice();
  let gas_estimate = await management.estimateGas.extractNativeValue(msg, proof, root, {} )

  const tx = await management.populateTransaction.extractNativeValue(msg, proof, root, {
    gasPrice: gasPrice, gasLimit: gas_estimate
  } )

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent:     ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(`Transaction received: ${txReceipt.transactionHash}`)

  const l1_cost = parseInt(txReceipt.gasUsed) * parseInt(txReceipt.effectiveGasPrice)
  console.log(`  L1 cost:       ${l1_cost}`)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--l2_network <value>', 'Connection URL to the L2 network')
  .option('--l2_bridge_address <value>', 'Contract address for the Ethereum Bridge')
  .option('--l2_bridge_abi <value>', 'Contract ABI file for the Ethereum Bridge')
  .option('--l2_bus_address <value>', 'Contract address for the L2 Message Bus')
  .option('--l2_bus_abi <value>', 'Contract ABI file for the L2 Message Bus')
  .option('--l1_network <value>', 'Connection URL to the L1 network')
  .option('--l1_management_address <value>', 'Contract address for the L1 Management Contract')
  .option('--l1_management_abi <value>', 'Contract ABI file for the L1 Management Contract')
  .option('--node_url <value>', 'The node url to make RPC calls against')
  .option('--pk <value>', 'The account private key')
  .option('--to <value>', 'The address to transfer to')
  .option('--amount <value>', 'The amount to transfer')
  .option('--timeout <value>', 'The timeout waiting on the transfer')
  .parse(process.argv)

const options = commander.opts()
var provider = new ethers.providers.JsonRpcProvider(options.l2_network)
var wallet = new ethers.Wallet(options.pk, provider)

var bridge_abi = JSON.parse(fs.readFileSync(options.l2_bridge_abi))
var bus_abi = JSON.parse(fs.readFileSync(options.l2_bus_abi))
var bridge_contract = new ethers.Contract(options.l2_bridge_address, bridge_abi, wallet)
var bus_contract = new ethers.Contract(options.l2_bus_address, bus_abi, wallet)

console.log('Starting transaction to send funds to the L1')
sendTransfer(provider, wallet, options.to, options.amount, bridge_contract, bus_contract).then( (arg1) => {
  var provider = new ethers.providers.JsonRpcProvider(options.l1_network)
  var wallet = new ethers.Wallet(options.pk, provider)
  var management_abi = JSON.parse(fs.readFileSync(options.l1_management_abi))
  var management_contract = new ethers.Contract(options.l1_management_address, management_abi, wallet)

  console.log('Waiting for the merkle tree root to be published on the L1')
  waitForRootPublished(options.node_url, arg1[1]).then( (arg2) => {

    console.log('Starting transaction to extract the native value L1')
    extractNativeValue(provider, wallet, management_contract, arg1[0], arg2[0], arg2[1]).then( () => {
      console.log(`Completed transactions`)
    })
  })
})

