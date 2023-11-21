const fs = require('fs')
const os = require("os")
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function sendTransaction(key, value) {
  fn_call = contract.methods.setItem(key, value)
  data = fn_call.encodeABI()
  gas_estimate = await fn_call.estimateGas({ from: sender_address })
  gas_price = await web3.eth.getGasPrice()
  tx_count = await web3.eth.getTransactionCount(sender_address)
  value_hex = web3.utils.toHex(value)
  value_padded_hex = web3.utils.padLeft(value_hex, 64)

  start_time = process.hrtime()

  params = {
    from: sender_address,
    to: options.contract_address,
    gas: gas_estimate,
    gasPrice: gas_price,
    data: data,
    nonce: tx_count,
  }
  signed_tx = await web3.eth.accounts.signTransaction(params, options.private_key)

  inputs = [{"indexed": true, "name": "key", "type": "string"}, {"indexed": true, "name": "value", "type": "uint256"}]

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
         log_time = process.hrtime(start_time)
         log_time_ms = (log_time[0] * 1000) + (log_time[1] / 1e6)
         decoded_data = web3.eth.abi.decodeLog(inputs, event.raw.data, event.raw.topics.slice(1))
         console.log('Decoded Event Data:', decoded_data.key, decoded_data.value)
         console.log('Completed transaction')
         fs.appendFile(options.output_file, log_time_ms.toString() + os.EOL, function (err) { if (err) throw err })
         sendTransaction(key, value+1)
       }
  })

  web3.eth.sendSignedTransaction(signed_tx.rawTransaction)
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
const json = fs.readFileSync(options.contract_abi)
const abi = JSON.parse(json)

const web3 = new Web3(`${options.network}`)
const contract = new web3.eth.Contract(abi, options.contract_address)
const sender_address = web3.eth.accounts.privateKeyToAccount(options.private_key).address
const indexed_string = web3.utils.sha3(options.key)
console.log('Indexed string:', indexed_string)

console.log('Starting transactions')
sendTransaction(options.key, 0)

