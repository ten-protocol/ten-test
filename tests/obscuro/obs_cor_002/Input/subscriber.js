const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  contract.events.allEvents({fromBlock:'latest'},
    function(error, result) {
      if (error) {
        console.log('Error returned:', error)
      } else {
        console.log('Received event:', result.event);
      }
    }
  )
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .option('--pk_to_register <value>', 'Private key used to register for a viewing key')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.contract_address}`)

let sign = (message) => { return web3.eth.accounts.sign(message, '0x' + options.pk_to_register) }
let address = web3.eth.accounts.privateKeyToAccount(options.pk_to_register).address
vk.generate_viewing_key(sign, options.network_http, address, task)









