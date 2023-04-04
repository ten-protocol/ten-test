const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  filter = {
    address: options.address,
    topics: [
      ethers.utils.id('ItemSet3(string,uint256)'),
      ethers.utils.id(options.filter_key)
    ]
  }
  provider.on(filter, (log, event) => {
    decoded_log = interface.decodeEventLog('ItemSet3', log.data, log.topics)
    console.log('Stored value =', decoded_log.value.toNumber())
  });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contract ABI file')
  .option('--filter_key <value>', 'Key to filter ony')
  .parse(process.argv)


const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.address, abi, provider)
const interface = new ethers.utils.Interface(abi)
task()


