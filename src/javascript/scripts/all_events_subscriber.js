// Subscribe to all events from a contract. Note that it is assumed the client / account has been registered
// outside the scope of this script e.g. for use against Ten.
//
const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

function subscribe() {
  console.log('Making subscription for contract events')
  contract.events.allEvents({fromBlock:'latest'},
    function(error, result) {
      if (error) {
        console.log('Error returned:', error)
      } else {
        console.log('Received event:', result.event)
        if (options.log_event) {
          console.log('Full event:', result)
        }
      }
    }
  )
  .on('connected', function(subscriptionId){
      console.log('Subscription confirmed with id:', subscriptionId)
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--log_event', 'Log the full event', false)
  .parse(process.argv)

const options = commander.opts()
var web3 = new Web3(options.network_ws)
var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, options.contract_address)
subscribe()








