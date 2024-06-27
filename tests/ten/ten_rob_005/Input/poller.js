const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

async function task() {
    let blockNumber = await web3.eth.getBlockNumber()
    let randomInt = getRandomInt(1, 4);

    switch (randomInt) {
        case 1:
            pollSimpleEvent(blockNumber-5)
            break;
        case 2:
            pollArrayEvent(blockNumber-5)
            break;
        case 3:
            pollStructEvent(blockNumber-5)
            break;
        case 4:
            pollMappingEvent(blockNumber-5)
            break;
        default:
            console.log("Out of range");
    }
}

function pollSimpleEvent(from) {
    console.log('Getting past SimpleEvent events from', from, 'to latest')
    setTimeout(function() {
      contract.getPastEvents('SimpleEvent', { fromBlock: from, toBlock: 'latest'})
      .then(function(events) {
          if (events.length) {
              console.log('  Events received =', events.length)
          }
          task(from)
      });
    }, 2000);
}

function pollArrayEvent(from) {
    console.log('Getting past ArrayEvent events from', from, 'to latest')
    setTimeout(function() {
      contract.getPastEvents('ArrayEvent', { fromBlock: from, toBlock: 'latest'})
      .then(function(events) {
          if (events.length) {
              console.log('  Events received =', events.length)
          }
          task(from)
      });
    }, 2000);
}

async function pollStructEvent(from) {
    console.log('Getting past StructEvent events from', from, 'to latest')
    setTimeout(function() {
      contract.getPastEvents('StructEvent', { fromBlock: from, toBlock: 'latest'})
      .then(function(events) {
          if (events.length) {
              console.log('  Events received =', events.length)
          }
          task(from)
      });
    }, 2000);
}

async function pollMappingEvent(from) {
    console.log('Getting past MappingEvent events from', from, 'to latest')
    setTimeout(function() {
      contract.getPastEvents('MappingEvent', { fromBlock: from, toBlock: 'latest'})
      .then(function(events) {
          if (events.length) {
              console.log('  Events received =', events.length)
          }
          task(from)
      });
    }, 2000);
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.contract_address}`)
task()


