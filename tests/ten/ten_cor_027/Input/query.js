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
    address: options.bus_address,
    topics: [
      ethers.utils.id('ValueTransfer(address,address,uint256,uint64)'),
      sender,
      receiver
    ]
  }
  provider.on(filter, (result) => {
    decoded_log = interface.decodeEventLog('ValueTransfer', result.data, result.topics)
    log(`Log transfer sender = ${decoded_log.sender}`)
    log(`Log transfer receiver = ${decoded_log.receiver}`)
    log(`Log transfer amount = ${decoded_log.amount.toNumber()}`)
    log(`Event log received`)
  });

  log(`Started task ...`)
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--bus_address <value>', 'Contract address')
  .option('--bus_abi <value>', 'Contract ABI file')
  .option('--sender_address <value>', 'Address of the sender')
  .option('--receiver_address <value>', 'Address of the received')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)


const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

const sender = ethers.utils.hexZeroPad(options.sender_address, 32);
const receiver = ethers.utils.hexZeroPad(options.receiver_address, 32);

var json = fs.readFileSync(options.bus_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.bus_address, abi, provider)
const interface = new ethers.utils.Interface(abi)
task()


