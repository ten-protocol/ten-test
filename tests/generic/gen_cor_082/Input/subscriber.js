const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function task() {
  log(`Starting task ...`)
  topic = web3.utils.sha3('ItemSet1(string,uint256)')
  inputs = [{"indexed": true, "name": "key", "type": "string"}, {"indexed": false, "name": "value", "type": "uint256"}]
  topics = [ topic, [web3.utils.sha3(options.filter_key1), web3.utils.sha3(options.filter_key2)] ]
  web3.eth.subscribe('logs', {
      topics: topics,
      address: options.address
    },
    function(error, result) {
      if (error) {
        log(`Error returned is ${error}`)
      } else {
        result = web3.eth.abi.decodeLog(inputs, result.data, result.topics)
        log(`Stored value = ${result.value}`)
      }
    }
  ) .on("connected", function(subscriptionId){
       log('Subscribed for event logs')
       log('Subscription id is', subscriptionId)
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--filter_key1 <value>', 'The first key value to filter on')
  .option('--filter_key2 <value>', 'The second key value to filter on')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)
task()











