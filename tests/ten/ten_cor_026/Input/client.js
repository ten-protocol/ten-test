const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')
const merkle = require('@openzeppelin/merkle-tree')
require('console-stamp')(console, 'HH:MM:ss')

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
function process_value_transfer(value_transfer) {
  const abiTypes = ['address', 'address', 'uint256', 'uint64'];
  const msg = [
    value_transfer['args'].sender, value_transfer['args'].receiver,
    value_transfer['args'].amount.toString(), value_transfer['args'].sequence.toString()
  ]
  const abiCoder = new ethers.utils.AbiCoder()
  const encodedMsg = abiCoder.encode(abiTypes, msg)
  return [msg, ethers.utils.keccak256(encodedMsg)]
}

/** Logic on the L2 side to initiate the transfer of funds to the L1 */
async function sendTransfer(provider, wallet, to, amount, bridge, bus) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await bridge.estimateGas.sendNative(to, { value: amount } );

  // send the transaction and get the block it is included into
  const tx = await bridge.populateTransaction.sendNative(to, {
    value: amount, gasPrice: gasPrice, gasLimit: estimatedGas
  } )

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent:     ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(`Transaction received: ${txReceipt.transactionHash}`)

  const block = await provider.send('eth_getBlockByHash', [txReceipt.blockHash, true]);
  console.log(`Block received:       ${block.number}`)

  // extract and log all the values, check that the msgHash is in the decoded tree
  const value_transfer = bus.interface.parseLog(txReceipt.logs[1]);
  const _processed_value_transfer = process_value_transfer(value_transfer)
  const msg = _processed_value_transfer[0]
  const msgHash = _processed_value_transfer[1]
  const decoded = decode_base64(block.crossChainTree)
  console.log(`  Sender:        ${value_transfer['args'].sender}`)
  console.log(`  Receiver:      ${value_transfer['args'].receiver}`)
  console.log(`  Amount:        ${value_transfer['args'].amount}`)
  console.log(`  Sequence:      ${value_transfer['args'].sequence}`)
  console.log(`  VTrans Hash:   ${msgHash}`)
  console.log(`  XChain tree:   ${decoded}`)
  console.log(`  Merkle root:   ${block.crossChainTreeHash}`)

  if (decoded[0][1] == msgHash) {
    console.log('Value transfer hash is in the xchain tree')
  }

  // construct the merkle tree, get the proof, check the root matches
  const tree = merkle.StandardMerkleTree.of(decoded, ["string", "bytes32"]);
  const proof = tree.getProof(['v',msgHash])
  console.log(`  Merkle root:   ${tree.root}`)
  console.log(`  Merkle proof:  ${proof[0]}`)

  if (block.crossChainTreeHash == tree.root) {
    console.log('Constructed merkle root matches block crossChainTreeHash')
  }

  return [msg, proof, tree.root]
}

/** Utility function to wait for the merkle root to be published on the L1 */
async function waitForRootPublished(management, msg, proof, root, interval = 5000, timeout = 2400000) {
  var gas_estimate = null
  const startTime = Date.now();

  while (gas_estimate === null) {
    try {
      gas_estimate = await management.estimateGas.ExtractNativeValue(msg, proof, root, {} )
    } catch (error) {
      console.log(`Estimate gas threw error : ${error.reason}`)
    }
    if (Date.now() - startTime >= timeout) {
      console.log(`Timed out waiting for the estimate gas to return`)
      break
    }
    await sleep(interval);
  }
  return gas_estimate
}

/** Logic on the L1 side to instruct the management contract to release funds */
async function extractNativeValue(provider, wallet, management, msg, proof, root, gas_estimate) {
  const gasPrice = await provider.getGasPrice();

  const tx = await management.populateTransaction.ExtractNativeValue(msg, proof, root, {
    gasPrice: gasPrice, gasLimit: gas_estimate
  } )

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent:     ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(`Transaction received: ${txReceipt.transactionHash}`)
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
  .option('--pk <value>', 'The account private key')
  .option('--to <value>', 'The address to transfer to')
  .option('--amount <value>', 'The amount to transfer')
  .parse(process.argv)

const options = commander.opts()
var provider = new ethers.providers.JsonRpcProvider(options.l2_network)
var wallet = new ethers.Wallet(options.pk, provider)

var bridge_abi = JSON.parse(fs.readFileSync(options.l2_bridge_abi))
var bus_abi = JSON.parse(fs.readFileSync(options.l2_bus_abi))
var bridge_contract = new ethers.Contract(options.l2_bridge_address, bridge_abi, wallet)
var bus_contract = new ethers.Contract(options.l2_bus_address, bus_abi, wallet)

console.log('Starting transaction to send funds to the L1')
sendTransfer(provider, wallet, options.to, options.amount, bridge_contract, bus_contract).then( (arg) => {
  var provider = new ethers.providers.JsonRpcProvider(options.l1_network)
  var wallet = new ethers.Wallet(options.pk, provider)
  var management_abi = JSON.parse(fs.readFileSync(options.l1_management_abi))
  var management_contract = new ethers.Contract(options.l1_management_address, management_abi, wallet)

  console.log('Waiting for the merkle tree root to be published on the L1')
  waitForRootPublished(management_contract, arg[0], arg[1], arg[2]).then( (estimate) => {
    console.log(`Estimate gas is: ${estimate}`)

    if (estimate != null) {
      console.log('Starting transaction to extract the native value L1')
      extractNativeValue(provider, wallet, management_contract, arg[0], arg[1], arg[2], estimate).then( () => {
        console.log(`Completed transactions`)
      })
    }
  })
})

