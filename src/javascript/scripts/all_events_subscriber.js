const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')
const reg = require('register.js')

require('console-stamp')(console, 'HH:MM:ss')

function subscribe() {
  contract.events.allEvents({fromBlock:'latest'},
    function(error, result) {
      if (error) {
        console.log('Error returned:', error)
      } else {
        console.log('Received event:', result.event);
        console.log('Full event:', result);
      }
    }
  )
  .on('connected', function(subscriptionId){
      console.log('Subscription confirmed with id:', subscriptionId);
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--host <value>', 'Http host')
  .option('--port <value>', 'Http port')
  .option('--user_id <value>', 'The user id')
  .option('--pk_to_register <value>', 'Private key')
  .parse(process.argv)

const options = commander.opts()
var web3_http = new Web3(options.network_http)
var web3_ws = new Web3(options.network_ws)
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new web3_ws.eth.Contract(abi, options.contract_address)
console.log(options.network_ws)

if (options.pk_to_register) {
  let sign = (message) => { return web3_http.eth.accounts.sign(message, '0x' + options.pk_to_register) }
  let address = web3_http.eth.accounts.privateKeyToAccount(options.pk_to_register).address
  reg.register(sign, options.host, options.port, options.user_id, address, subscribe)
}
else
  subscribe()








