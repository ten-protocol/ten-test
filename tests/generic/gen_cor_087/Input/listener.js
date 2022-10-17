const fs = require('fs')
const ethers = require('ethers')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  task1()
}

function task1() {
  filter = {
    address: options.contract_address,
    topics: [
      ethers.utils.id('ItemSet3(string,uint256,address)'),
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
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--contract_address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .option('--filter_key <value>', 'Key to filter ony')
  .option('--pk_to_register <value>', 'Private key used to register for a viewing key (obscuro only)')
  .parse(process.argv)


const options = commander.opts()
const provider = new ethers.providers.WebSocketProvider(options.network_ws)
console.log(options.filter_keys)

var json = fs.readFileSync(options.contract_abi)
var abi = JSON.parse(json)
const contract = new ethers.Contract(options.contract_address, abi, provider)
const interface = new ethers.utils.Interface(abi)

if (options.pk_to_register) {
  wallet = new ethers.Wallet(options.pk_to_register)
  address = wallet.getAddress()
  vk.generate_viewing_key(web3, options.network_http, address, options.pk_to_register, task)
}
else {
  task()
}

