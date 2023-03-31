const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  topic = web3.utils.sha3('CallerIndexedAddress(address)')
  topics = [ topic ]
  web3.eth.subscribe('logs', {
      topics: topics
    },
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        console.log('Result = ', result)
      }
    }
  ) .on("connected", function(subscriptionId){
       console.log('Subscribed for event logs')
       console.log('Subscription id is', subscriptionId)
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'The externally owned address to filter on')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)
task()











