const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function pollSimpleEvent() {
    log(`Getting past SimpleEvent events from 0 to latest, id filter ${options.id_filter}`)
    setTimeout(function() {
      contract.getPastEvents('SimpleEvent', {
          fromBlock: 0,
          toBlock: 'latest',
          filter: {id: options.id_filter}
          })
      .then(function(events) {
          if (events.length) {
              log(`  Events received = ${events.length}`)
          }
          pollSimpleEvent()
      });
    }, 2000);
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--id_filter <value>', 'The id index field')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.contract_address}`)
pollSimpleEvent()


