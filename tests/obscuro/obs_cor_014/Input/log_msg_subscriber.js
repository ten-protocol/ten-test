const Web3 = require('web3')
const commander = require('commander')
const vk = require('viewing_key.js')

require('console-stamp')(console, 'HH:MM:ss')

function task() {
  console.log('Starting task ...')
  inputs =
    [
      {"indexed": false,"internalType": "address", "name": "sender", "type": "address"},
      {"indexed": false,"internalType": "uint64", "name": "sequence", "type": "uint64"},
      {"indexed": false,"internalType": "uint32","name": "nonce","type": "uint32"},
      {"indexed": false,"internalType": "uint32","name": "topic","type": "uint32"},
      {"indexed": false,"internalType": "bytes","name": "payload","type": "bytes" },
      {"indexed": false,"internalType": "uint8","name": "consistencyLevel", "type": "uint8"}
    ]
  topic = [ web3.utils.sha3('LogMessagePublished(address,uint64,uint32,uint32,bytes,uint8)') ]
  web3.eth.subscribe('logs', {
      topics: topic
    },
    function(error, result) {
      if (error) {
        console.log('Error returned is ', error)
      } else {
        result = web3.eth.abi.decodeLog(inputs, result.data, result.topics)
        console.log('Sender =', result.sender)
        console.log('Sequence =', result.sequence)
        console.log('Nonce =', result.nonce)
        console.log('Topic =', result.topic)
        console.log('Payload =', result.payload)
        console.log('ConsistencyLevel =', result.consistencyLevel)
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
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .parse(process.argv)

const options = commander.opts()
const web3 = new Web3(`${options.network_ws}`)
task()










