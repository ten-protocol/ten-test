const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString();
    const entry = `${timestamp} ${data}\n`;
    fs.appendFileSync(options.log_file, entry, { flag: 'a' });
}

function task() {
  filter = {
    address: options.bridge_address,
    topics: [ ethers.utils.id('LogMessagePublished(address,uint64,uint32,uint32,bytes,uint8)') ]
  }
  provider.on(filter, (result) => {
    decoded_log = interface.decodeEventLog('LogMessagePublished', result.data, result.topics)
    log(`Decoded log = ${decoded_log}`)
    log(`Event log received`)
  });

  log(`Started task ...`)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'Contract address')
  .option('--abi <value>', 'Contract ABI file')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)


const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

var json = fs.readFileSync(options.abi)
var _abi = JSON.parse(json)
const contract = new ethers.Contract(options.address, _abi, provider)
const interface = new ethers.utils.Interface(_abi)
task()


