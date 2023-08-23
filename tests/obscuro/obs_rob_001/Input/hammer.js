const Web3 = require('web3')
const http = require('http')
const commander = require('commander')

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
      setTimeout(function() { unsubscribe() }, 50);
  })
  .on("data", function(log){})
}

function unsubscribe() {
  console.log('Unsubscribing for event logs')
  subscription.unsubscribe(function(error, success){
    if (success) {
        console.log('Successfully unsubscribed')
        setTimeout(function() { subscribe() }, 50);
    }
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .parse(process.argv)

// in global scope the options, web3 connection and server reference
var subscription = null
const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)
subscribe()
