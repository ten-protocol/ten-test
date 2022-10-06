const Web3 = require('web3')
const commander = require('commander')
const fs = require('fs')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function get_balance() {
  web3.eth.getBalance(address,
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        //this should only pass if the viewing key was registered successfully
        console.log('Account balance is', result)
        console.log('Starting to run the polling loop')
        task();
      }
    }
  )
}

function task() {
  setTimeout(function() {
    contract.methods.balanceOf(address).call(
      function(error, result) {
        if (error) {
          console.log('Error returned is ', error)
        } else {
          console.log('New balance =', result)
          task(contract, address);
        }
     })
  }, 2000);
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--contract_address <value>', 'Web socket connection URL to the network')
  .option('--contract_abi <value>', 'Web socket connection URL to the network')
  .option('--private_key <value>', 'Private key for the account')
  .option('--is_obscuro', 'True if running against obscuro', false)
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_http}`)

var json = fs.readFileSync(`${options.contract_abi}`)
var abi = JSON.parse(json)
const contract = new web3.eth.Contract(abi, `${options.contract_address}`)
const address = web3.eth.accounts.privateKeyToAccount(options.private_key).address

if (options.is_obscuro == true) {
  vk.generate_viewing_key(web3, options.network_http, address, options.private_key, get_balance)
}
else {
  get_balance()
}








