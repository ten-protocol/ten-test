const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  contract.on("Stored", (value, event) => {
    console.log('Stored value =', value.toNumber())
  });
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .option('--pk_to_register <value>', 'Private key used to register for a viewing key (obscuro only)')
  .parse(process.argv)

const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)

var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.address, abi, provider)
const interface = new ethers.utils.Interface(abi)

if (options.pk_to_register) {
  wallet = new ethers.Wallet('0x' + options.pk_to_register)
  let sign = (message) => { return wallet.signMessage(message) }
  let address = wallet.getAddress()
  vk.generate_viewing_key(sign, options.network_http, address, task)
}
else {
  task()
}

