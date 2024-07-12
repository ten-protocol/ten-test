const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function task(address) {
  log(`Starting subscription for address ${address}`)
  topic = web3.utils.sha3('IndexedAddressAndNumber(address,uint256)')
  topics = [ topic, address ]
  web3.eth.subscribe('logs', {
      topics: topics
    },
    function(error, result) {
      if (error) {
        log(`Error returned is ${error}`)
      } else {
        log(`Result = ${Web3.utils.hexToNumber(result.data)}`)
      }
    }
  ) .on("connected", function(subscriptionId){
       log(`Subscribed for event logs`)
       log(`Subscription id is ${subscriptionId}`)
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'The externally owned address to filter on')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

address = `${web3.utils.padLeft('0x', 24)}${options.address.split('0x')[1]}`
task(address)










