const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function task(from) {
   log('Getting past TwoIndexedAddresses events from ' + from + ' to latest')
   contract.getPastEvents('TwoIndexedAddresses', { fromBlock: from, toBlock: 'latest'}).then(function(events) {
    if (events.length) {
      for (var i = 0, len = events.length; i < len; i+=1) {
        log('TwoIndexedAddresses event:')
        log('  addr1 = ' + events[i].returnValues['addr1'])
        log('  addr2 = ' + events[i].returnValues['addr2'])
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
task(options.from_block)


