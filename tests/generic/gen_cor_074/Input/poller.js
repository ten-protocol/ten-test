const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  task1(0)
  task2(0)
  task3(0)
  console.log('Started tasks')
}

function task1(from) {
  setTimeout(function() {
    contract.getPastEvents('ItemSet1', {
      fromBlock: from,
      toBlock: 'latest',
      filter: {setter: options.filter_address}
    })
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                key = events[i].returnValues['key']
                value = events[i].returnValues['value']
                console.log('Task1:', key, value)
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
                console.log('Task2:', key, value)
                from = events[i].blockNumber+1
            }
        }
        task2(from)
    })
  }, 1000)
}

function task3(from) {
  setTimeout(function() {
    contract.getPastEvents('ItemSet3', {
      fromBlock: from,
      toBlock: 'latest',
      topics: [web3.utils.sha3('ItemSet3(string,uint256,address)'), web3.utils.sha3(options.filter_key)]
    })
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                value = events[i].returnValues['value']
                console.log('Task3:', value)
                from = events[i].blockNumber+1
            }
        }
        task3(from)
    })
  }, 1000)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .option('--filter_address <value>', 'Web socket connection URL to the network')
  .option('--filter_key <value>', 'Web socket connection URL to the network')
  .option('--pk_to_register <value>', 'Private key used to register for a viewing key (obscuro only)')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.contract_address}`)

if (options.pk_to_register) {
  address = web3.eth.accounts.privateKeyToAccount(options.pk_to_register).address
  vk.generate_viewing_key(web3, options.network_http, address, options.pk_to_register, task)
}
else {
  task()
}




