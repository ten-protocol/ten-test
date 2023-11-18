const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function sendTransaction() {
  const functionCall = contract.methods.setItem(options.key, options.value)
  const gasEstimate = await functionCall.estimateGas({ from: sender_address })
  const gasPrice = await web3.eth.getGasPrice()

  const transactionParameters = {
    from: sender_address,
    to: options.contract_address,
    gas: gasEstimate,
    gasPrice: gasPrice,
    data: functionCall.encodeABI(),
    nonce: await web3.eth.getTransactionCount(sender_address),
  }
  console.log('Transaction created')

  const value_hex = web3.utils.toHex(options.value);
  const value_padded_hex = web3.utils.padLeft(value_hex, 64);

  contract.once('ItemSet3', {
    fromBlock: 'latest',
    topics: [
       web3.utils.sha3('ItemSet3(string,uint256)'),
       web3.utils.sha3(options.key),
       value_padded_hex]
   },
    function(error, event){
       if (error) {
         console.log('Error returned is ', error)
       } else {
         console.log(event)
         console.log('Completed transactions')
       }
  })

  const signedTransaction = await web3.eth.accounts.signTransaction(transactionParameters, options.private_key);
  const txReceipt = await web3.eth.sendSignedTransaction(signedTransaction.rawTransaction)
  console.log(`Transaction status: ${txReceipt.status}`)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--private_key <value>', 'The account private key')
  .option('--key <value>', 'The key to store against')
  .option('--value <value>', 'The value to store against the key')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

const web3 = new Web3(`${options.network}`)
const contract = new web3.eth.Contract(abi, options.contract_address)
const sender_address = web3.eth.accounts.privateKeyToAccount(options.private_key).address

console.log('Starting transactions')
sendTransaction()

