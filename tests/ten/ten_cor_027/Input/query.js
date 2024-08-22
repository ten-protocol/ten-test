const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

async function task() {
    log(`Getting past SimpleEvent events from ${from} to latest, id filter ${options.id_filter}`)
    topic = web3.utils.sha3('SimpleEvent(uint,string,address)')
    contract.getPastEvents('SimpleEvent', {
          fromBlock: 0,
          toBlock: 'latest',
          filter: {id: options.id_filter}
          })
    .then(function(events) {
     if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                log(events[i])
            }
          }
          log(`Poller completed`)
      });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.contract_address}`)
task()


