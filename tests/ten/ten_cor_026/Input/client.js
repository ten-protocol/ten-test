const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

function get_message_hash(value_transfer) {
  const abiTypes = ['address', 'address', 'uint256', 'uint64'];
  const msg = [
    value_transfer['args'].sender, value_transfer['args'].receiver,
    value_transfer['args'].amount, value_transfer['args'].sequence
  ];
  const abiCoder = new ethers.utils.AbiCoder()
  const encodedMsg = abiCoder.encode(abiTypes, msg)
  return ethers.utils.keccak256(encodedMsg)
}

function decode_tree(base64String) {
  let jsonString = atob(base64String);
  return JSON.parse(jsonString);
}

async function sendTransaction(to, amount) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await bridge_contract.estimateGas.sendNative(options.to, { value: options.amount } );

  // send the transaction and get the block it is included into
  const tx = await bridge_contract.populateTransaction.sendNative(options.to, {
    value: options.amount, gasPrice: gasPrice, gasLimit: estimatedGas,
  } )

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent:     ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(`Transaction received: ${txReceipt.transactionHash}`)

  const block = await provider.send('eth_getBlockByNumber', [ethers.utils.hexValue(txReceipt.blockNumber), true]);
  console.log(`Block received:       ${block.number}`)

  // extract and log all the values
  const value_transfer = bus_contract.interface.parseLog(txReceipt.logs[0]);
  const msgHash = get_message_hash(value_transfer)
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
}


commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--bridge_address <value>', 'Contract address for the Ethereum Bridge')
  .option('--bridge_abi <value>', 'Contract ABI file for the Ethereum Bridge')
  .option('--bus_address <value>', 'Contract address for the L2 Message Bus')
  .option('--bus_abi <value>', 'Contract ABI file for the L2 Message Bus')
  .option('--sender_pk <value>', 'The account private key')
  .option('--to <value>', 'The address to transfer to')
  .option('--amount <value>', 'The amount to transfer')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.sender_pk, provider)

var bridge_abi = JSON.parse(fs.readFileSync(options.bridge_abi))
var bus_abi = JSON.parse(fs.readFileSync(options.bus_abi))
const bridge_contract = new ethers.Contract(options.bridge_address, bridge_abi, wallet)
const bus_contract = new ethers.Contract(options.bus_address, bus_abi, wallet)

console.log(`Starting transactions`)
sendTransaction(options.to, options.amount).then(() => console.log(`Completed transactions`));

