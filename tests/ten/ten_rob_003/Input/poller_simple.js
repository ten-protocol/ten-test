const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function task() {
    pollSimpleEvent(0)
}

function pollSimpleEvent(from) {
    console.log('Getting past SimpleEvent events from', from, 'to latest, id filter', options.id_filter)
    setTimeout(function() {
      contract.getPastEvents('SimpleEvent', {
          fromBlock: from,
          toBlock: 'latest',
          filter: {id: options.id_filter}
          })
      .then(function(events) {
          if (events.length) {
              console.log('  Events received =', events.length)
          }
          pollSimpleEvent(0)
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
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.contract_address}`)
task()


