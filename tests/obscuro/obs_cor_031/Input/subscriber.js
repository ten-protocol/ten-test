const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

function subscribe() {
  subscription = web3.eth.subscribe('logs', [],
    function(error, result) {
      if (error)
        console.log('Error returned is ', error)
  })
  .on("connected", function(subscriptionId){
      console.log('Subscribed for event logs')
      console.log('Subscription id is', subscription.id)
      console.log('Subscription arguments are', subscription.arguments)
  })
  .on("data", function(log){
      console.log('Stored value =', Web3.utils.hexToNumber(log.data))
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)
subscribe()









