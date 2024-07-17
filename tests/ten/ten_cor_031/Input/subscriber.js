const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function subscribe() {
  subscription = web3.eth.subscribe('logs', {},
    function(error, result) {
      if (error)
        log(`Error returned is ${error}`)
  })
  .on("connected", function(subscriptionId){
      log(`Subscribed for event logs`)
      log(`Subscription id is ${subscription.id}`)
      log(`Subscription arguments are ${subscription.arguments}`)
  })
  .on("data", function(event){
      value = Web3.utils.hexToNumber(event.data)
      log(`Stored value = ${value}`)
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)
subscribe()









