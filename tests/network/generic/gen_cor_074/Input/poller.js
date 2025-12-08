const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function task() {
  task1(0)
  task2(0)
  log(`Started tasks`)
}

function task1(from) {
  setTimeout(function() {
    contract.getPastEvents('ItemSet1', {
      fromBlock: from,
      toBlock: 'latest',
      topics: [web3.utils.sha3('ItemSet1(string,uint256)'), web3.utils.sha3(options.filter_key)]
    })
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                value = events[i].returnValues['value']
                log(`Task1: ${value}`)
                from = events[i].blockNumber+1
            }
        }
        task1(from)
    })
  }, 1000)
}

function task2(from) {
  setTimeout(function() {
    contract.getPastEvents('ItemSet2', {
      fromBlock: from,
      toBlock: 'latest',
      filter: {value: [2,3]}
    })
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                key = events[i].returnValues['key']
                value = events[i].returnValues['value']
                log(`Task2: ${key} ${value}`)
                from = events[i].blockNumber+1
            }
        }
        task2(from)
    })
  }, 1000)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI path')
  .option('--filter_address <value>', 'Address to filter on')
  .option('--filter_key <value>', 'Key to filter on')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.address}`)
task()




