const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

var block_count = 0

function task(address) {
  log(`Starting task ...`)
  web3.eth.subscribe('newBlockHeaders',
    function(error, result) {
      if (error) {
        log(`Error returned is ${error}`)
      } else {
        block_count = block_count + 1
        if (block_count <= 4) {
          log(`Block = ${result}`)
        }
      }
    }
  ).on("connected", function(subscriptionId){
       log(`Subscribed for newBlockHeaders`)
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

task()










