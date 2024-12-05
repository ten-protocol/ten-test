const fs = require('fs')
const Web3 = require('web3')
const commander = require('commander')

function log(data) {
    let timestamp = new Date().toISOString()
    const entry = `${timestamp} ${data}\n`
    fs.appendFileSync(options.log_file, entry, { flag: 'a' })
}

function task() {
  log('Starting task ...')
  contract.events.CallerIndexedAddress({fromBlock:'latest'},
    function(error, result) {
      if (error) {
        log(`Error returned is ${error}`)
      } else {
        const decodedLog = web3.eth.abi.decodeLog(
           eventInputs,
           result.raw.data,
           result.raw.topics.slice(1)
         )
         log(`Decoded address = ${decodedLog.addr}`)
      }
    }
  )
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'Contract address')
  .option('--contract_abi <value>', 'Contrat ABI file')
  .option('--log_file <value>', 'The output file to write to')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const event = abi.find(item => item.type === 'event' && item.name === 'CallerIndexedAddress')
const eventInputs = event ? event.inputs : null
const contract = new web3.eth.Contract(abi, `${options.address}`)
task()

















