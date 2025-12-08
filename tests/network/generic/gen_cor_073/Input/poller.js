const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function task() {
  log('Starting task ...')
  task1(0)
}

function task1(from) {
  log('Getting past events from ' + from + ' to latest')
  setTimeout(function() {
    contract.getPastEvents('Stored', { fromBlock: from, toBlock: 'latest'})
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                log('Stored value = ' + events[i].returnValues['value'])
                log('Block number of event log is ' + events[i].blockNumber)
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
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'The contract address')
  .option('--contract_abi <value>', 'The contract ABI file')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.address}`)
task()


