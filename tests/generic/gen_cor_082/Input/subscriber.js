const Web3 = require('web3')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  topic = web3.utils.sha3('ItemSet3(string,uint256,address)')
  inputs = [{"indexed": true, "name": "key", "type": "string"}, {"indexed": false, "name": "value", "type": "uint256"}, {"indexed": false, "name": "setter", "type": "address"}]
  topics = [ topic, [web3.utils.sha3(options.filter_key1), web3.utils.sha3(options.filter_key2)] ]
  web3.eth.subscribe('logs', {
      topics: topics,
      address: options.address
    },
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        result = web3.eth.abi.decodeLog(inputs, result.data, result.topics)
        console.log('Stored value =', result.value)
      }
    }
  )
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--filter_address <value>', 'The contract address to filter on')
  .option('--filter_key1 <value>', 'The first key value to filter on')
  .option('--filter_key2 <value>', 'The second key value to filter on')
  .option('--pk_to_register <value>', 'Private key used to register for a viewing key (obscuro only)', null)
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

if (options.pk_to_register) {
  let sign = (message) => { return web3.eth.accounts.sign(message, '0x' + options.pk_to_register) }
  let address = web3.eth.accounts.privateKeyToAccount(options.pk_to_register).address
  vk.generate_viewing_key(sign, options.network_http, address, task)
}
else {
  task()
}










