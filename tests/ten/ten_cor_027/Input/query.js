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
  filter = {
    address: options.contract_address,
    topics: [
      ethers.utils.id('ValueTransfer(address,address,uint256,uint64)')
    ]
  }
  provider.on(filter, (result) => {
    decoded_log = interface.decodeEventLog('ValueTransfer', result.data, result.topics)
    log(`Log transfer receiver = ${decoded_log.receiver}`)
    log(`Log transfer amount = ${decoded_log.amount.toNumber()}`)
  });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)


const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.contract_address, abi, provider)
const interface = new ethers.utils.Interface(abi)
task()


