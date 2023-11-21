const fs = require('fs')
const os = require("os")
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

function subscribe() {
  inputs = [{"indexed": true, "name": "key", "type": "string"}, {"indexed": true, "name": "value", "type": "uint256"}]

  contract.events.ItemSet3(
  {
    fromBlock: 'latest',
    topics: [
       web3.utils.sha3('ItemSet3(string,uint256)'),
       web3.utils.sha3(options.key)]
   },
    function(error, event){
       if (error) {
         console.log('Error returned is ', error)
       } else {
         decoded_data = web3.eth.abi.decodeLog(inputs, event.raw.data, event.raw.topics.slice(1))
         start_time = send_times[decoded_data.value]
         log_time = process.hrtime(start_time)
         log_time_ms = log_time[0] + (log_time[1] / 1e9)
         fs.appendFile(options.event_log, decoded_data.value.toString() + " " + log_time_ms.toString() + os.EOL, function (err) { if (err) throw err })
       }
  })
}

async function sendTransaction(key, value) {
  fn_call = contract.methods.setItem(key, value)
  data = fn_call.encodeABI()
  gas_estimate = await fn_call.estimateGas({ from: sender_address })
  gas_price = await web3.eth.getGasPrice()
  tx_count = await web3.eth.getTransactionCount(sender_address)

  start_time = process.hrtime()
  send_times[value] = start_time

  params = {
    from: sender_address,
    to: options.contract_address,
    gas: gas_estimate,
    gasPrice: gas_price,
    data: data,
    nonce: tx_count,
  }
  signed_tx = await web3.eth.accounts.signTransaction(params, options.private_key)
  tx_receipt = await web3.eth.sendSignedTransaction(signed_tx.rawTransaction)
  
  receipt_time = process.hrtime(start_time)
  receipt_time_ms = receipt_time[0] + (receipt_time[1] / 1e9)
  fs.appendFile(options.receipt_log, value.toString() + " " + receipt_time_ms.toString() + os.EOL, function (err) { if (err) throw err })
  sendTransaction(key, value+1)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network <value>', 'Connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--private_key <value>', 'The account private key')
  .option('--key <value>', 'The key to store against')
  .option('--event_log <value>', 'File to log the latency for event logs to')
  .option('--receipt_log <value>', 'File to log the latency for transaction receipts to')
  .parse(process.argv)

const options = commander.opts()
const json = fs.readFileSync(options.contract_abi)
const abi = JSON.parse(json)

const web3 = new Web3(`${options.network}`)
const contract = new web3.eth.Contract(abi, options.contract_address)
const sender_address = web3.eth.accounts.privateKeyToAccount(options.private_key).address
const indexed_string = web3.utils.sha3(options.key)
console.log('Indexed string:', indexed_string)
const send_times = {}

console.log('Starting transactions')
subscribe()
sendTransaction(options.key, 0)

