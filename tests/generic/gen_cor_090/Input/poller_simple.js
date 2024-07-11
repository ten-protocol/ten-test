const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

async function task() {
    pollSimpleEvent(0)
}

function pollSimpleEvent(from) {
    log(`Getting past SimpleEvent events from ${from} to latest, id filter ${options.id_filter}`)
    topic = web3.utils.sha3('SimpleEvent(uint,string,address)')
    setTimeout(function() {
      contract.getPastEvents('SimpleEvent', {
          fromBlock: from,
          toBlock: 'latest',
          filter: {id: options.id_filter}
          })
      .then(function(events) {
          if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                log(`Event: id= ${events[i].returnValues['id']} message= ${events[i].returnValues['message']}`)
            }
          }
          log(`Poller completed`)
      });
    }, 2000);
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .option('--id_filter <value>', 'The id index field')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.contract_address}`)
task()


