const Web3 = require('web3')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  inputs =
    [
    {"indexed": false,"internalType": "address","name": "remoteAddress","type": "address"},
    {"indexed": false,"internalType": "address","name": "localAddress","type": "address"},
    {"indexed": false,"internalType": "string","name": "name","type": "string"},
    {"indexed": false,"internalType": "string","name": "symbol","type": "string"}
    ]
  topic = [ web3.utils.sha3('CreatedWrappedToken(address,address,string,string)') ]
  web3.eth.subscribe('logs', {
      topics: topic
    },
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        result = web3.eth.abi.decodeLog(inputs, result.data, result.topics)
        console.log('RemoteAddress =', result.remoteAddress)
        console.log('LocalAddress =', result.localAddress)
        console.log('Name =', result.name)
        console.log('Type =', result.type)
      }
    }
  ) .on("connected", function(subscriptionId){
       console.log('Subscribed for event logs')
       console.log('Subscription id is', subscriptionId)
  })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--pk_to_register <value>', 'Private key used to register for a viewing key')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)

let sign = (message) => { return web3.eth.accounts.sign(message, '0x' + options.pk_to_register) }
let address = web3.eth.accounts.privateKeyToAccount(options.pk_to_register).address
vk.generate_viewing_key(sign, options.network_http, address, task)










