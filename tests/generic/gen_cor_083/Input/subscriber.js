const Web3 = require('web3')
const commander = require('commander')
const http = require('http')

function decodeLog(log) {
  console.log('Full log is ', log)
  console.log('Stored value =', Web3.utils.hexToNumber(log.data))
}

function subscribe() {
  dict = []
  if (options.filter_from_block) dict["fromBlock"] = options.filter_from_block
  if (options.filter_address) dict["address"] = options.filter_address
  if (options.filter_topics) dict["topics"] = options.filter_topics
  console.log('Options: ', dict)

  subscription = web3.eth.subscribe('logs', dict,
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

function generate_viewing_key(web3, network_url, address, private_key, callback) {
  console.log('Generating viewing key for', private_key)
  console.log(network_url + '/generateviewingkey/')

  fetch(network_url +'/generateviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({address: address})
  })
  .then(response => response.text())
  .then((response) => {
         sign_viewing_key(web3, network_url, address, private_key, callback, response)
   })
}

function sign_viewing_key(web3, network_url, address, private_key, callback, response) {
  console.log('Signing viewing key for', private_key)
  signed_msg = web3.eth.accounts.sign('vk' + response, '0x' + private_key)

  fetch(network_url + '/submitviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify( {signature: signed_msg.signature, address: address})
  })
  .then(response => response.text())
  .then((response) => {
    callback()
   })
}

function get_options() {
  commander
    .version('1.0.0', '-v, --version')
    .usage('[OPTIONS]...')
    .option('--script_server_port <value>', 'This script listening port for HTTP posts')
    .option('--network_http <value>', 'Http connection URL to the network')
    .option('--network_ws <value>', 'Web socket connection URL to the network')
    .option('--filter_address <value>', 'The contract address to filter on', null)
    .option('--filter_from_block <value>', 'The from block to filter on', null)
    .option('--filter_topics <values...>', 'The first filter topic', null)
    .option('--pk_to_register <value>', 'Private key used to register for a viewing key (obscuro only)', null)
    .parse(process.argv)

    return commander.opts()
}

// in global scope the options, web3 connection and server reference
const options = get_options()
const web3 = new Web3(`${options.network_ws}`)

// if pk supplied generate viewing key else just run
if (options.register_vk) {
  address = web3.eth.accounts.privateKeyToAccount(private_key).address
  generate_viewing_key(web3, options.network_http, address, options.pk_to_register, startServer)
}
else
  startServer()