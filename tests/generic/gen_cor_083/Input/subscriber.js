const Web3 = require('web3');
const commander = require('commander');
const http = require('http')

function subscribe() {
  topic = web3.utils.sha3('Stored(uint256)');
  subscription = web3.eth.subscribe('logs', {
    topics: [topic],
    address: options.contract_address
  }, function(error, result) {
       if (error)
         console.log('Error returned is ', error)
  })
  .on("connected", function(subscriptionId){
      console.log('Subscribed for event logs')
      console.log('Subscription id is', subscription.id);
      console.log('Subscription arguments are', subscription.arguments)
  })
  .on("data", function(log){
      console.log('Full log is ', log);
      console.log('Stored value =', Web3.utils.hexToNumber(log.data));
  })
}

function unsubscribe() {
  subscription.unsubscribe(function(error, success){
    if (success)
        console.log('Unsubscribed for event logs');
  });
}

function createServer(){
  var server = http.createServer(
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
  return server
}

function generate_viewing_key() {
  console.log('Generating viewing key for', options.account_private_key)
  console.log(options.network_http + '/generateviewingkey/')

  fetch(options.network_http +'/generateviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify({address: account.address})
  })
  .then(response => response.text())
  .then((response) => {
         sign_viewing_key()
   })
}

function sign_viewing_key() {
  console.log('Signing viewing key for', options.account_private_key)
  console.log('Result was', response)
  signed_msg = web3.eth.accounts.sign('vk' + response, '0x' + options.account_private_key)

  fetch(options.network_http + '/submitviewingkey/', {
    method: 'POST',
    headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
    body: JSON.stringify( {signature: signed_msg.signature, address: account.address})
  })
  .then(response => response.text())
  .then((response) => {
    console.log('Starting task ...')
    task()
   })
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-p, --script_server_port <value>', 'This script listening port for HTTP posts')
  .option('-u, --network_http <value>', 'Http connection URL to the network')
  .option('-w, --network_ws <value>', 'Web socket connection URL to the network')
  .option('-a, --contract_address <value>', 'Address of the contract to subscribe to')
  .option('-p, --account_private_key <value>', 'Private key for the account')
  .option('-o, --is_obscuro', 'True if running against obscuro', false)
  .parse(process.argv);

// options
const options = commander.opts();

// subscription is initially null
var subscription = null

// create the server to listen for subscription instructions
const server = createServer()

const web3 = new Web3(`${options.network_ws}`);
const account = web3.eth.accounts.privateKeyToAccount(`${options.account_private_key}`)

if (options.is_obscuro == true) {
  generate_viewing_key()
  server.listen(options.script_server_port, '127.0.0.1')
  console.log('Subscriber listening for instructions')
}
else {
  server.listen(options.script_server_port, '127.0.0.1')
  console.log('Subscriber listening for instructions')
}