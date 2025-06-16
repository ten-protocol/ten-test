const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

async function task() {
    pollSimpleEvent1(0)
}

function pollSimpleEvent1(from) {
    console.log('Getting (1) past SimpleEvent events from', from, 'to latest, id filter', options.id_filter)
    setTimeout(function() {
      contract1.getPastEvents('SimpleEvent', {
          fromBlock: from,
          toBlock: 'latest',
          filter: {id: options.id_filter}
          })
      .then(function(events) {
          if (events.length) {
              console.log('  Events received =', events.length)
          }
          pollSimpleEvent2(0)
      });
    }, 2000);
}

function pollSimpleEvent2(from) {
    console.log('Getting (2) past SimpleEvent events from', from, 'to latest, id filter', options.id_filter)
    setTimeout(function() {
      contract2.getPastEvents('SimpleEvent', {
          fromBlock: from,
          toBlock: 'latest',
          filter: {id: options.id_filter}
          })
      .then(function(events) {
          if (events.length) {
              console.log('  Events received =', events.length)
          }
          pollSimpleEvent1(0)
      });
    }, 2000);
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract1_address <value>', 'Contract address')
  .option('--contract1_abi <value>', 'Contract ABI file')
  .option('--contract2_address <value>', 'Contract address')
  .option('--contract2_abi <value>', 'Contract ABI file')
  .option('--id_filter <value>', 'The id index field')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract1_abi}`)
var abi = JSON.parse(json)
const contract1 = new web3.eth.Contract(abi, `${options.contract1_address}`)

var json = fs.readFileSync(`${options.contract2_abi}`)
var abi = JSON.parse(json)
const contract2 = new web3.eth.Contract(abi, `${options.contract2_address}`)
task()


