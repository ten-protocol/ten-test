const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')


async function sendTransaction(to, amount) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await bridge_contract.estimateGas.sendNative(options.to, { value: options.amount } );
  console.log('Command line arguments: ')
  console.log(`  Wallet address: ${wallet.address}`)
  console.log(`  Gas Price:      ${gasPrice}`)
  console.log(`  Estimated Gas:  ${estimatedGas}`)

  const tx = await bridge_contract.populateTransaction.sendNative(options.to, {
    value: options.amount,
    gasPrice: gasPrice,
    gasLimit: estimatedGas,
  } )
  console.log(`Transaction created`)

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(`Transaction received: ${txReceipt.transactionHash}`)

  console.log('Parsing value transfer event: ')
  const value_transfer = bus_contract.interface.parseLog(txReceipt.logs[0]);
  console.log(`  Sender:   ${value_transfer["args"].sender}`);
  console.log(`  Sequence: ${value_transfer["args"].sequence}`);
  console.log(`  Receiver: ${value_transfer["args"].receiver}`);
  console.log(`  Amount:   ${value_transfer["args"].amount}`);
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
console.log('Command line arguments: ')
console.log(`  Network URL:    ${options.network}`)
console.log(`  Bridge_address: ${options.bridge_address}`)
console.log(`  Bus_address:    ${options.bus_address}`)
console.log(`  To:             ${options.to}`)
console.log(`  Amount:         ${options.amount}`)

const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.sender_pk, provider)

var bridge_abi = JSON.parse(fs.readFileSync(options.bridge_abi))
const bridge_contract = new ethers.Contract(options.bridge_address, bridge_abi, wallet)

var bus_abi = JSON.parse(fs.readFileSync(options.bus_abi))
const bus_contract = new ethers.Contract(options.bus_address, bus_abi, wallet)

console.log(`Starting transactions`)
sendTransaction(options.to, options.amount).then(() => console.log(`Completed transactions`));

