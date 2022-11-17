const Web3 = require('web3')
const http = require('http')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function subscribe() {
  console.log('Subscribing for event logs')
  subscription = web3.eth.subscribe('logs', [],
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      }
  })
  .on("connected", function(subscriptionId){
      console.log('Successfully unsubscribed with id', subscription.id)
      unsubscribe()
  })
  .on("data", function(log){})
}

function unsubscribe() {
  console.log('Unsubscribing for event logs')
  subscription.unsubscribe(function(error, success){
    if (success) {
        console.log('Successfully unsubscribed')
        subscribe()
    }
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--pk_to_register <value>', 'Private key used to register for a viewing key', null)
  .parse(process.argv)

// in global scope the options, web3 connection and server reference
var subscription = null
const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

let sign = (message) => { return web3.eth.accounts.sign(message, '0x' + options.pk_to_register) }
let address = web3.eth.accounts.privateKeyToAccount(options.pk_to_register).address
vk.generate_viewing_key(sign, options.network_http, address, subscribe)
