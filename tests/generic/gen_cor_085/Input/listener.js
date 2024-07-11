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
  contract.on("Stored", (value, event) => {
    log(`Stored value = ${value.toNumber()}`)
  });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.address, abi, provider)
const interface = new ethers.utils.Interface(abi)
task()

