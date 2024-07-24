const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')
const merkle = require('@openzeppelin/merkle-tree')

function process_transfer(value_transfer) {
  const abiTypes = ['address', 'address', 'uint256', 'uint64'];
  const msg = [
    value_transfer['args'].sender, value_transfer['args'].receiver,
    value_transfer['args'].amount, value_transfer['args'].sequence
  ];
  const abiCoder = new ethers.utils.AbiCoder()
  const encodedMsg = abiCoder.encode(abiTypes, msg)
  return [msg, ethers.utils.keccak256(encodedMsg)]
}

function decode_tree(base64String) {
  let jsonString = atob(base64String);
  return JSON.parse(jsonString);
}

async function sendTransfer(provider, wallet, to, amount, bridge, bus) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await bridge.estimateGas.sendNative(to, { value: amount } );

  // send the transaction and get the block it is included into
  const tx = await bridge.populateTransaction.sendNative(to, {
    value: amount, gasPrice: gasPrice, gasLimit: estimatedGas,
  } )

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent:     ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(`Transaction received: ${txReceipt.transactionHash}`)

  const block = await provider.send('eth_getBlockByHash', [txReceipt.blockHash, true]);
  console.log(`Block received:       ${block.number}`)

  // extract and log all the values, check that the msgHash is in the decoded tree
  const value_transfer = bus.interface.parseLog(txReceipt.logs[0]);
  const _processed_value_transfer = process_transfer(value_transfer)
  const msg = _processed_value_transfer[0]
  const msgHash = _processed_value_transfer[1]
  const decoded = decode_tree(block.crossChainTree)
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

  return [msg, proof[0], tree.root]
}

async function extractNativeValue(provider, wallet, management, msg, proof, root) {
  //const gasPrice = await provider.getGasPrice();
  //const estimatedGas = await management.estimateGas.ExtractNativeValue(msg, proof, root, {} );
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

console.log(`Starting transactions`)
sendTransfer(provider, wallet, options.to, options.amount, bridge_contract, bus_contract).then((arg) => {
  var provider = new ethers.providers.JsonRpcProvider(options.l1_network)
  var wallet = new ethers.Wallet(options.pk, provider)
  var management_abi = JSON.parse(fs.readFileSync(options.l1_management_abi))
  var management_contract = new ethers.Contract(options.l1_management_address, management_abi, wallet)

  extractNativeValue(provider, wallet, management_contract, arg[0], arg[1], arg[2]).then(() => {
      console.log(`Completed transactions`)
  })
})

