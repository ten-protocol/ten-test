const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  task1(0)
}

function task1(from) {
  console.log('Getting past events from', from, 'to latest')
  setTimeout(function() {
    contract.getPastEvents('Stored', { fromBlock: from, toBlock: 'latest'})
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                console.log('Stored value =', events[i].returnValues['value'])
                console.log('Block number of event log is  ', events[i].blockNumber)
                from = events[i].blockNumber+1
            }
        }
        task1(from)
    });
  }, 2000);
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .option('--pk_to_register <value>', 'Private key used to register for a viewing key (obscuro only)')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.address}`)

if (options.pk_to_register) {
  let sign = (message) => { return web3.eth.accounts.sign(message, '0x' + options.pk_to_register) }
  let address = web3.eth.accounts.privateKeyToAccount(options.pk_to_register).address
  vk.generate_viewing_key(sign, options.network_http, address, task)
}
else {
  task()
}

