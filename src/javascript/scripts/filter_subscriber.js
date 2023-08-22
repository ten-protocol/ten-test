const Web3 = require('web3')
const http = require('http')
const commander = require('commander')
const reg = require('register.js')

function decodeLog(log) {
  //console.log('Full log: ', log)
  console.log('Stored value =', Web3.utils.hexToNumber(log.data))
}

function subscribe() {
  dict = []
  if (options.filter_from_block) dict["fromBlock"] = options.filter_from_block
  if (options.filter_address) dict["address"] = options.filter_address
  if (options.filter_topics) dict["topics"] = filter_topics
  console.log('Options: ', dict)

  subscription = web3_ws.eth.subscribe('logs', dict,
    function(error, result) {
      if (error)
        console.log('Error returned is ', error)
  })
  .on("connected", function(subscriptionId){
      console.log('Subscribed for event logs')
      console.log('Subscription id is', subscription.id)
      console.log('Subscription arguments are', subscription.arguments)
  })
  .on("data", function(log){
      decodeLog(log)
  })
}

function unsubscribe() {
  subscription.unsubscribe(function(error, success){
    if (success)
        console.log('Unsubscribed for event logs')
  })
}

function startServer(){
  const server = http.createServer(
    function(request, response) {
      if (request.method == 'POST') {
        var body = ''
        request.on('data', function(data) {
          body += data
        })
        request.on('end', function() {
          if (body == 'SUBSCRIBE'){
            subscribe()
          } else if (body == 'UNSUBSCRIBE'){
            unsubscribe()
          }
          response.writeHead(200, {'Content-Type': 'text/plain'})
          response.end('post received')
        })
      }
    }
  )
  server.listen(options.script_server_port, '127.0.0.1')
  console.log('Subscriber listening for instructions')
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('--script_server_port <value>', 'This script listening port for HTTP posts')
  .option('--network_http <value>', 'Http connection URL to the network')
  .option('--network_ws <value>', 'Web socket connection URL to the network')
  .option('--filter_address <value>', 'The contract address to filter on', null)
  .option('--filter_from_block <value>', 'The from block to filter on', null)
  .option('--filter_topics <values...>', 'The first filter topic', null)
  .option('--host <value>', 'Http host')
  .option('--port <value>', 'Http port')
  .option('--user_id <value>', 'The user id')
  .option('--pk_to_register <value>', 'Private key')
  .parse(process.argv)

// in global scope the options, web3 connection and server reference
var subscription = null
const options = commander.opts()
var web3_http = new Web3(options.network_http)
const web3_ws = new Web3(options.network_ws)
filter_topics = (options.filter_topics + '').split(' ')

// if pk supplied generate viewing key else just run
if (options.pk_to_register) {
  let account = web3_http.eth.accounts.privateKeyToAccount(options.pk_to_register)
  let sign = (message) => { return web3_http.eth.accounts.sign(message, account.privateKey) }
  reg.register(sign, options.host, options.port, options.user_id, account.address, startServer)
}
else
  startServer()