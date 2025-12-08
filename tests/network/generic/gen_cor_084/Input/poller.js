const fs = require('fs')
const ethers = require('ethers')
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
  setTimeout(async function() {
    log(`Getting past events from ${from} to latest`)
    const events = await contract.queryFilter('Stored', from, 'latest')
    if (events.length) {
      for (var i = 0, len = events.length; i < len; i+=1) {
        decoded_event = interface.decodeEventLog('Stored', events[i].data, events[i].topics)
        log(`Stored value = ${decoded_event.value.toNumber()}`)
        log(`Block number of event log is ${events[i].blockNumber}`)
        from = events[i].blockNumber+1
      }
    }
    task1(from)
  }, 2000)
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

