const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function sendTransaction() {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await contract.estimateGas.setItem(options.key, options.value);
  console.log(`Wallet address: ${wallet.address}`)
  console.log(`Gas Price: ${gasPrice}`)
  console.log(`Estimated Gas: ${estimatedGas}`)

  const tx = await contract.populateTransaction.setItem(options.key, options.value, {
    from: wallet.address,
    gasPrice: gasPrice,
    gasLimit: estimatedGas,
  } )
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
  .option('--address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--private_key <value>', 'The account private key')
  .option('--key <value>', 'The key to store against')
  .option('--value <value>', 'The value to store against the key')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.private_key, provider)
const contract = new ethers.Contract(options.address, abi, wallet)

console.log('Starting transactions')
sendTransaction().then(() => console.log('Completed transactions'));

