
const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

async function sendTransaction(to, amount) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await contract.estimateGas.sendNative(options.to, { value: options.amount } );
  console.log(`Wallet address: ${wallet.address}`)
  console.log(`Gas Price: ${gasPrice}`)
  console.log(`Estimated Gas: ${estimatedGas}`)

  const tx = await contract.populateTransaction.sendNative(options.to, {
    value: options.amount,
    gasPrice: gasPrice,
    gasLimit: estimatedGas,
  } )
  console.log(`Transaction created`)

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(txReceipt)
const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

async function sendTransaction(to, amount) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await contract.estimateGas.sendNative(options.to, { value: options.amount } );
  console.log(`Wallet address: ${wallet.address}`)
  console.log(`Gas Price: ${gasPrice}`)
  console.log(`Estimated Gas: ${estimatedGas}`)

  const tx = await contract.populateTransaction.sendNative(options.to, {
    value: options.amount,
    gasPrice: gasPrice,
    gasLimit: estimatedGas,
  } )
  console.log(`Transaction created`)

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(txReceipt)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--sender_pk <value>', 'The account private key')
  .option('--to <value>', 'The address to transfer to')
  .option('--amount <value>', 'The amount to transfer')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

console.log(`Network URL: ${options.network}`)
const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.sender_pk, provider)
const contract = new ethers.Contract(options.contract_address, abi, wallet)

console.log(`Starting transactions`)
sendTransaction(options.to, options.amount).then(() => console.log(`Completed transactions`));

const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

async function sendTransaction(to, amount) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await contract.estimateGas.sendNative(options.to, { value: options.amount } );
  console.log(`Wallet address: ${wallet.address}`)
  console.log(`Gas Price: ${gasPrice}`)
  console.log(`Estimated Gas: ${estimatedGas}`)

  const tx = await contract.populateTransaction.sendNative(options.to, {
    value: options.amount,
    gasPrice: gasPrice,
    gasLimit: estimatedGas,
  } )
  console.log(`Transaction created`)

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(txReceipt)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--sender_pk <value>', 'The account private key')
  .option('--to <value>', 'The address to transfer to')
  .option('--amount <value>', 'The amount to transfer')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

console.log(`Network URL: ${options.network}`)
const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.sender_pk, provider)
const contract = new ethers.Contract(options.contract_address, abi, wallet)

console.log(`Starting transactions`)
sendTransaction(options.to, options.amount).then(() => console.log(`Completed transactions`));

const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

async function sendTransaction(to, amount) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await contract.estimateGas.sendNative(options.to, { value: options.amount } );
  console.log(`Wallet address: ${wallet.address}`)
  console.log(`Gas Price: ${gasPrice}`)
  console.log(`Estimated Gas: ${estimatedGas}`)

  const tx = await contract.populateTransaction.sendNative(options.to, {
    value: options.amount,
    gasPrice: gasPrice,
    gasLimit: estimatedGas,
  } )
  console.log(`Transaction created`)

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(txReceipt)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--sender_pk <value>', 'The account private key')
  .option('--to <value>', 'The address to transfer to')
  .option('--amount <value>', 'The amount to transfer')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

console.log(`Network URL: ${options.network}`)
const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.sender_pk, provider)
const contract = new ethers.Contract(options.contract_address, abi, wallet)

console.log(`Starting transactions`)
sendTransaction(options.to, options.amount).then(() => console.log(`Completed transactions`));

const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

async function sendTransaction(to, amount) {
  const gasPrice = await provider.getGasPrice();
  const estimatedGas = await contract.estimateGas.sendNative(options.to, { value: options.amount } );
  console.log(`Wallet address: ${wallet.address}`)
  console.log(`Gas Price: ${gasPrice}`)
  console.log(`Estimated Gas: ${estimatedGas}`)

  const tx = await contract.populateTransaction.sendNative(options.to, {
    value: options.amount,
    gasPrice: gasPrice,
    gasLimit: estimatedGas,
  } )
  console.log(`Transaction created`)

  const txResponse = await wallet.sendTransaction(tx)
  console.log(`Transaction sent: ${txResponse.hash}`)

  const txReceipt = await txResponse.wait();
  console.log(txReceipt)

  txReceipt.logs.forEach((log) => {
    try {
      const parsedLog = contract.interface.parseLog(log);
      console.log(parsedLog);
    } catch (error) {
       // Handle the case where the log does not match the contract's events
    }
  });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--sender_pk <value>', 'The account private key')
  .option('--to <value>', 'The address to transfer to')
  .option('--amount <value>', 'The amount to transfer')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

console.log(`Network URL: ${options.network}`)
const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.sender_pk, provider)
const contract = new ethers.Contract(options.contract_address, abi, wallet)

console.log(`Starting transactions`)
sendTransaction(options.to, options.amount).then(() => console.log(`Completed transactions`));

}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--sender_pk <value>', 'The account private key')
  .option('--to <value>', 'The address to transfer to')
  .option('--amount <value>', 'The amount to transfer')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

console.log(`Network URL: ${options.network}`)
const provider = new ethers.providers.JsonRpcProvider(options.network)
const wallet = new ethers.Wallet(options.sender_pk, provider)
const contract = new ethers.Contract(options.contract_address, abi, wallet)

console.log(`Starting transactions`)
sendTransaction(options.to, options.amount).then(() => console.log(`Completed transactions`));
