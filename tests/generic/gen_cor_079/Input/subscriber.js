const Web3 = require('web3')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  web3.eth.subscribe('logs', {
      topics: [web3.utils.sha3('Stored(uint256)')]
    },
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        console.log('Full result is ', result)
        console.log('Stored value =', Web3.utils.hexToNumber(result.data))
      }
    }
  )
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--pk_to_register <value>', 'Private key used to register for a viewing key (obscuro only)')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

if (options.pk_to_register == true) {
  address = web3.eth.accounts.privateKeyToAccount(options.pk_to_register).address
  vk.generate_viewing_key(web3, options.network_http, address, options.pk_to_register, task)
}
else {
  task()
}










