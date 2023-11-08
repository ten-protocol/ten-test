const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function sendTransaction() {
  const tx = await contract.populateTransaction.setItem('Key', 1, { gasLimit: 400000 } )
  console.log('Transaction created')

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(`Transaction status: ${txReceipt.status}`)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--private_key <value>', 'The account private key')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

const provider = new ethers.providers.WebSocketProvider(options.network_ws)
const wallet = new ethers.Wallet(options.private_key, provider)
const contract = new ethers.Contract(options.address, abi, wallet)

console.log('Starting transactions')
sendTransaction().then(() => console.log('Completed transactions'));

