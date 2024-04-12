const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

var block_count = 0

function task(address) {
  console.log('Starting task ...')
  web3.eth.subscribe('newBlockHeaders',
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        block_count = block_count + 1
        if (block_count <= 4) {
          console.log('Block =', result)
        }
      }
    }
  ).on("connected", function(subscriptionId){
       console.log('Subscribed for newBlockHeaders')
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

task()










