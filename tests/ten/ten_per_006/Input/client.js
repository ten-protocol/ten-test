const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function sendTransaction(key, value) {
  functionCall = contract.methods.setItem(key, value)
  gasEstimate = await functionCall.estimateGas({ from: sender_address })
  gasPrice = await web3.eth.getGasPrice()

  transactionParameters = {
    from: sender_address,
    to: options.contract_address,
    gas: gasEstimate,
    gasPrice: gasPrice,
    data: functionCall.encodeABI(),
    nonce: await web3.eth.getTransactionCount(sender_address),
  }
  signedTransaction = await web3.eth.accounts.signTransaction(transactionParameters, options.private_key)

  value_hex = web3.utils.toHex(value)
  value_padded_hex = web3.utils.padLeft(value_hex, 64)
  startTime = process.hrtime()

  contract.once('ItemSet3', {
    fromBlock: 'latest',
    topics: [
       web3.utils.sha3('ItemSet3(string,uint256)'),
       web3.utils.sha3(key),
       value_padded_hex]
   },
    function(error, event){
       if (error) {
         console.log('Error returned is ', error)
       } else {
         endTime = process.hrtime(startTime)
         elapsedTimeMilliseconds = (endTime[0] * 1000) + (endTime[1] / 1e6)
         console.log(`Elapsed time: ${elapsedTimeMilliseconds} milliseconds`)
         console.log('Completed transaction')
         sendTransaction(key, value+1)
       }
  })

  txReceipt = await web3.eth.sendSignedTransaction(signedTransaction.rawTransaction)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--private_key <value>', 'The account private key')
  .option('--key <value>', 'The key to store against')
  .option('--output_file <value>', 'File to log the results to')
  .parse(process.argv)

const options = commander.opts()
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)

const web3 = new Web3(`${options.network}`)
const contract = new web3.eth.Contract(abi, options.contract_address)
const sender_address = web3.eth.accounts.privateKeyToAccount(options.private_key).address

console.log('Starting transactions')
sendTransaction(options.key, 0)

