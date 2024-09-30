const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function task1(from) {
   log('Getting past Guessed events from ' + from + ' to latest')
   contract.getPastEvents('Guessed', { fromBlock: from, toBlock: 'latest'}).then(function(events) {
    if (events.length) {
      for (var i = 0, len = events.length; i < len; i+=1) {
        log('Guessed event:')
        log('  user = ' + events[i].returnValues['user'])
        log('  guessedNumber = ' + events[i].returnValues['guessedNumber'])
        log('  success = ' + events[i].returnValues['success'])
        log('  secretNumber = ' + events[i].returnValues['secretNumber'])
       }
    }
    task2(from)
  })
}

function task2(from) {
   log('Getting past Attempts events from ' + from + ' to latest')
   contract.getPastEvents('Attempts', { fromBlock: from, toBlock: 'latest'}).then(function(events) {
    if (events.length) {
      for (var i = 0, len = events.length; i < len; i+=1) {
        log('Attempts event:')
        log('  user = ' + events[i].returnValues['user'])
        log('  attempts = ' + events[i].returnValues['attempts'])
       }
    }
    log('Completed task')
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'The contract address')
  .option('--contract_abi <value>', 'The contract ABI file')
  .option('--log_file <value>', 'The output file to write to')
  .option('--from_block <value>', 'Get events from this block to latest')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.address}`)
task1(options.from_block)


