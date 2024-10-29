const fs = require('fs')
const os = require("os")
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function sendTransaction(key, value) {
  // the function being called on the contract
  fn_call = contract.methods.setItem(key, value)
  data = fn_call.encodeABI()

  // get the gas details and nonce
  gas_estimate = await fn_call.estimateGas({ from: sender_address })
  gas_price = await web3.eth.getGasPrice()
  tx_count = await web3.eth.getTransactionCount(sender_address)

  // the value to filter on needs to be left padded as a hex
  value_hex = web3.utils.toHex(value)
  value_padded_hex = web3.utils.padLeft(value_hex, 64)

  // the params to the transaction for the function
  params = {
    from: sender_address,
    to: options.contract_address,
    gas: gas_estimate,
    gasPrice: gas_price,
    data: data,
    nonce: tx_count,
  }
  signed_tx = await web3.eth.accounts.signTransaction(params, options.private_key)

  // listen once for this event, and when received send the next with a monotonically increasing value to the key
  contract.once('ItemSet3', {
    fromBlock: 'latest',
    topics: [
       web3.utils.sha3('ItemSet3(string,uint256)'),
       web3.utils.sha3(key),
       value_padded_hex]
   },
    function(error, event){
       if (error) {
         stats[1] += 1
         console.log('Error returned is ', error)
       } else {
         stats[0] += 1
         log_time = Number(process.hrtime.bigint() - start_time) / 1e9
         fs.appendFile(options.output_file, log_time.toString() + os.EOL, function (err) { if (err) throw err })
         if (value <= iterations) {
            sendTransaction(key, value+1)
         }
         else {
            console.log('Ratio failures =', ( stats[1] / (stats[0]+stats[1])).toFixed(2) )
            console.log('Completed transactions')
         }
       }
  })

  // set the start time before immediately sending the signed transaction
  start_time = process.hrtime.bigint()
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
  .option('--num_iterations <value>', 'The number of iterations')
  .parse(process.argv)

const options = commander.opts()
const json = fs.readFileSync(options.contract_abi)
const abi = JSON.parse(json)

const web3 = new Web3(`${options.network}`)
const contract = new web3.eth.Contract(abi, options.contract_address)
const sender_address = web3.eth.accounts.privateKeyToAccount(options.private_key).address
const iterations = parseInt(options.num_iterations)
let stats = [0,0]

console.log('Starting transactions')
sendTransaction(options.key, 0)