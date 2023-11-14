const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function sendTransaction() {
  const gasPrice = await provider.getGasPrice()
  console.log(`Wallet address: ${wallet.address}`)
  console.log(`Gas Price: ${gasPrice}`)

  const tx = {
    to: options.to,
    value: options.amount,
    gasLimit: 21000,
    gasPrice: gasPrice,
  }
  console.log('Transaction created')

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(`Transaction status: ${txReceipt.status}`)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--private_key <value>', 'The account private key')
  .option('--to <value>', 'The address to send funds to')
  .option('--amount <value>', 'The amount of funds to send')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.private_key, provider)

console.log('Starting transactions')
sendTransaction().then(() => console.log('Completed transactions'));

