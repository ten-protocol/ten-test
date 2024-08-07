const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function task() {
  log(`Starting task ...`)
  task1()
  task2()
}

function task1() {
  filter = contract.filters.ItemSet1(options.filter_key, null)
  contract.on(filter, (key, value, event) => {
    log(`ItemSet1, key = ${options.filter_key} stored value = ${value.toNumber()}`)
  });
}

function task2() {
  filter = contract.filters.ItemSet2(null, options.filter_value)
  contract.on(filter, (key, value, event) => {
    log(`ItemSet2, key = ${key} stored value = ${value.toNumber()}`)
  });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'The contract address')
  .option('--contract_abi <value>', 'The contract ABI')
  .option('--filter_value <value>', 'Value to filter on')
  .option('--filter_key <value>', 'Key to filter on')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.address, abi, provider)
const interface = new ethers.utils.Interface(abi)
task()

